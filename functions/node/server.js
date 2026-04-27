#!/usr/bin/env node

const net = require("net");
const fs = require("fs");
const { execSync } = require("child_process");

// ---- emulate rdtsc with nanosecond timestamp ----
function getCycles() {
    return Number(process.hrtime.bigint()); // nanoseconds
}

// ---- helper to run shell commands ----
function run(cmd, quiet = false) {
    if (!quiet) {
        console.log(cmd);
    }
    return execSync(cmd, { encoding: "utf8" });
}

// ---- main TCP server ----
const server = net.createServer((conn) => {
    let buffer = "";

    conn.on("data", async (data) => {
        buffer += data.toString();

        try {
            let funcArgs = JSON.parse(buffer);
            let funcName = funcArgs.function;

            if (
                funcName === "chameleon" ||
                funcName === "pyaes"
            ) {
                funcName = funcName + "1";
            }

            if (funcArgs.disable_sanpage) {
                try {
                    run(
                        "echo 8 > /proc/sys/vm/drop_caches",
                    );
                } catch (err) {
                    console.error(
                        "drop_caches failed:",
                        err.message,
                    );
                }
            }

            // ---- dynamically import handler ----
            // expects modules like ./chameleon1/chameleon1.js exporting function_handler
            let handlerModule = require(`./${funcName}.js`);
            let handler = handlerModule.function_handler;

            let ret = await handler(funcArgs);

            funcArgs.end_tsc = getCycles();
            let response = JSON.stringify(funcArgs);

            conn.write(response);
            conn.end();
        } catch (err) {
            console.error("Error:", err);
            conn.write(err.stack || err.toString());
            conn.end();
        }
    });
});

server.listen(5003, "0.0.0.0", () => {
    console.log("Server listening on 127.0.0.1:5003");
});
