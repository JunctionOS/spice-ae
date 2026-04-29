import org.json.JSONObject;

import java.io.*;
import java.lang.reflect.Method;
import java.nio.file.*;
import java.util.Scanner;

public class Runner {

    // static {
    //     // Load libc for malloc_trim
    //     System.loadLibrary("c");  // Or use JNA/JNI properly on your system
    // }

    // Native method declaration (via JNI or JNA)
    // public static native void malloc_trim(int pad);

    public static void snapshotPrepare() {
        System.out.flush();
        for (int i = 0; i < 3; i++) {
            System.gc();
        }

        // try {
            // malloc_trim(0);
        // } catch (UnsatisfiedLinkError e) {
        //     System.err.println("malloc_trim not available or not linked.");
        // }
    }

    public static void run(Method handler, Object instance) throws Exception {
        BufferedReader reader = new BufferedReader(new FileReader("/serverless/chan0"));
        PrintWriter writer = new PrintWriter(new FileOutputStream("serverless/chan0"));

        while (true) {
            String cmd = reader.readLine();

            if (cmd.equals("SNAPSHOT_PREPARE")) {
                snapshotPrepare();
                writer.write("OK");
                writer.flush();
                continue;
            }

            JSONObject jsonReq = new JSONObject(cmd);
            Object result = handler.invoke(instance, jsonReq);
            writer.write("test");
            writer.flush();
        }
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

    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.err.println("Usage: java Runner <name>");
            return;
        }

        String name = args[0];
        String prog = name;

        if (name.equals("chameleon") || name.equals("pyaes")) {
            prog = name + "1";
        }

        String className = prog + "." + toCamelCase(prog);
        Class<?> clazz = Class.forName(className);
        Method handler = clazz.getMethod("handler", JSONObject.class);
        Object instance = clazz.getDeclaredConstructor().newInstance();

        run(handler, instance);
    }

    private static String capitalize(String s) {
        if (s.isEmpty()) return s;
        return Character.toUpperCase(s.charAt(0)) + s.substring(1);
    }
}
