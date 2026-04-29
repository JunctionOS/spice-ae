#!/usr/bin/env node
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const rdtsc = require("./rdtsc/build/Release/rdtsc.node");
import path from "path";
import { fileURLToPath } from "url";

const WARMUP_ITERS = 10;
const __dirname = path.dirname(
    fileURLToPath(import.meta.url),
);

if (process.argv.length < 4) {
    console.error(
        "Usage: node criu_runner.mjs <prog> <json_string>",
    );
    process.exit(1);
}

let prog = process.argv[2];
const jsonString = process.argv[3];
const jsonReq = JSON.parse(jsonString);

if (prog === "chameleon" || prog === "pyaes") {
    prog += "1";
}

const { function_handler: main } = require(prog);

const warmups = [];
for (let i = 0; i < WARMUP_ITERS; i++) {
    const start = rdtsc.getCycles();
    const ret = await main(jsonReq);
    console.log(ret);
    const end = rdtsc.getCycles();
    warmups.push(end - start);
}

console.log("looping\n");
const now = Date.now();
while (Date.now() - now < 10_000) {}
console.log("done looping\n");

let start = rdtsc.getCycles();
await main(jsonReq);
let end = rdtsc.getCycles();
const cold = end - start;

console.log(
    "DATA",
    JSON.stringify({
        warmup: warmups,
        cold,
        program: process.argv[2],
    }),
);

console.log(`iteration finish: ${rdtsc.getCycles()}`);
process.exit(0);
