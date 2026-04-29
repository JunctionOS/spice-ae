cmd_Release/rdtsc.node := ln -f "Release/obj.target/rdtsc.node" "Release/rdtsc.node" 2>/dev/null || (rm -rf "Release/rdtsc.node" && cp -af "Release/obj.target/rdtsc.node" "Release/rdtsc.node")
