const sharp = require('sharp');
const fs = require('fs');
const path = require('path');
const Minio = require("minio");
const { promisify } = require("util");

const TMP = "/tmp/"

function parseAddress(addr) {
  const [host, port] = addr.split(":");
  return { host, port: parseInt(port, 10) };
}

async function resize(arg) {
    try {

        const {host, port} = parseAddress(arg.minio_addr)
        const image = arg.image

        const minioClient = new Minio.Client({
            endPoint: host,
            port: port,
            useSSL: false,
            accessKey: "minioadmin",
            secretKey: "minioadmin"
        });

        const fGetObjectAsync = promisify(minioClient.fGetObject).bind(minioClient);
        await fGetObjectAsync("mybucket", image, TMP + "/" + image);
        const data = await fs.promises.readFile(TMP + "/" + image);
        await sharp(data)
            .rotate(90)
            .toFile(TMP + "/out");
    } catch (err) {
        await console.log(err);
    }
}

async function function_handler(arg) {
    await resize(arg);
    return " ";
}

module.exports = { function_handler };
