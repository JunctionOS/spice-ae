import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import org.json.JSONObject;
import java.lang.reflect.Method;
import java.lang.reflect.InvocationTargetException;

public class SimpleServer {
    static int port = 5001;

    public static String readToEnd(InputStream in) throws IOException {
        ByteArrayOutputStream buffer = new ByteArrayOutputStream();

        byte[] data = new byte[1024];
        int n;
        int len = 0;
        // StringBuilder sb = new StringBuilder();
        while (in.available() > 0) {
            n = in.read(data);
            len += n;
            System.out.println(n);
            buffer.write(data, 0, n);
        }

        byte[] result = buffer.toByteArray();

        return new String(result, StandardCharsets.UTF_8);
    }

    public static String toCamelCase(String snake) {
        StringBuilder result = new StringBuilder();

        String[] parts = snake.split("_");

        for (int i = 0; i < parts.length; i++) {
            String part = parts[i];
            if (!part.isEmpty()) {
                result.append(part.substring(0, 1).toUpperCase());
                result.append(part.substring(1));
            }
        }

        return result.toString();
    }

    public static void disableSanpage() {
        try (FileWriter writer = new FileWriter("/proc/sys/vm/drop_caches")) {
            writer.write("8\n");
            writer.flush();
            System.out.println("Successfully dropped caches.");
        } catch (IOException e) {
            System.err.println("Failed to drop caches: " + e.getMessage());
        }
    }

    public static void main(String[] args) throws IOException {
        System.out.println("Starting server");
        Method handler = null;
        Object instance = null;
        JSONObject funcArgs = null;
        ServerSocket serverSocket = new ServerSocket(port);
        // try (ServerSocket serverSocket = new ServerSocket(port)) {
        while (true) {
            Socket socket = serverSocket.accept();

            InputStream input = socket.getInputStream();
            BufferedReader reader = new BufferedReader(new InputStreamReader(input));

            OutputStream output = socket.getOutputStream();
            PrintWriter writer = new PrintWriter(output, true);

            String text = readToEnd(input).strip().strip();
            try {
                if (text.length() > 1) {
                    funcArgs = new JSONObject(text);

                    if (handler == null) {
                        String funcName = funcArgs.getString("function");
                        String className = funcName + "." + toCamelCase(funcName);
                        Class<?> clazz = Class.forName(className);
                        handler = clazz.getMethod("handler", JSONObject.class);
                        instance = clazz.getDeclaredConstructor().newInstance();
                    }
                }

                if (funcArgs.getBoolean("disable_sanpage")) {
                    disableSanpage();
                    text += "disabled sanpage ";
                } else {
                    long start = System.nanoTime();
                    handler.invoke(instance, funcArgs);
                    long time = System.nanoTime() - start;
                    text += "invocation took: " + time / 1000;
                }
            } catch (InvocationTargetException e) {
                text = e.getCause().toString();
            } catch (Exception e) {
                text = e.toString();
            }

            writer.println(text);
            socket.close();
        }
        // } catch (Exception e) {
        //     System.out.println("Server exception: " + e.getMessage());
        // }
    }
}
