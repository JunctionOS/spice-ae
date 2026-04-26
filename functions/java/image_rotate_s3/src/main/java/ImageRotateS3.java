package image_rotate_s3;

import java.io.InputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.awt.image.BufferedImage;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import io.minio.MinioClient;
import io.minio.GetObjectArgs;
import javax.imageio.ImageIO;
import org.json.JSONObject;

public class ImageRotateS3 {
    public void rotate(BufferedImage image, double angle) {
        int width = image.getWidth();
        int height = image.getHeight();
        int newWidth =
            (int) Math.abs(width * Math.cos(angle) + height * Math.sin(angle));
        int newHeight =
            (int) Math.abs(width * Math.sin(angle) + height * Math.cos(angle));

        BufferedImage rotatedImage =
            new BufferedImage(newWidth, newHeight, image.getType());
        Graphics2D g2d = rotatedImage.createGraphics();

        g2d.setRenderingHint(RenderingHints.KEY_INTERPOLATION,
                             RenderingHints.VALUE_INTERPOLATION_BILINEAR);

        g2d.translate((newWidth - width) / 2, (newHeight - height) / 2);
        g2d.rotate(angle, width / 2.0, height / 2.0);
        g2d.drawImage(image, 0, 0, null);

        g2d.dispose();

        try {
            Boolean ret =
                ImageIO.write(rotatedImage,
                              "jpg",
                              new FileOutputStream("/tmp/image.jpg"));

        } catch (IOException e) {
            System.out.println("Failed to write image");
        }
    }

    public void handler(JSONObject args) {
        String minioAddr = (String)args.get("minio_addr");
        String img = (String)args.get("image");

        MinioClient client = MinioClient.builder()
            .endpoint("http://" + minioAddr)
            .credentials("minioadmin", "minioadmin")
            .build();

        BufferedImage image;
        BufferedImage rotated;

        double angle = Math.toRadians(90);

        try(InputStream stream =
            client.getObject(GetObjectArgs.builder()
                             .bucket("mybucket")
                             .object(img)
                             .build())) {
            image = ImageIO.read(stream);
            this.rotate(image, angle);
        } catch (Exception e) {
            System.out.println(e);
        }
    }
}
