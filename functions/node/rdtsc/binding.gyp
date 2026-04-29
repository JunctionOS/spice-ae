{
  "targets": [
    {
      "target_name": "rdtsc",
      "sources": [ "rdtsc.cpp" ],
      "include_dirs": [
        "<!(node -e \"require('nan')\")"
      ]
    }
  ]
}
