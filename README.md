# Rothko TWRP GitHub Actions Builder

Cloud builder for the experimental Xiaomi 14T Pro / Redmi K70 Ultra (`rothko`)
TWRP Android 16 device tree by JonesqPacMan.

## Run

1. Create a new GitHub repository.
2. Upload the contents of this ZIP to the repository root, preserving `.github/workflows/build-twrp.yml`.
3. Open **Actions** → **Build Rothko TWRP** → **Run workflow**.
4. When the job finishes, download the `rothko-twrp-build` artifact.

If the build fails, the artifact should still contain `build.log`.

## Important

Do NOT flash the generated `vendor_boot.img` directly yet.

The intended next step is to inspect/extract the compiled TWRP recovery ramdisk and
merge it into the known-good stock OS3.0.301 vendor_boot while preserving the
phone's stock platform ramdisk, DTB, bootconfig, and command line.

The final merged image must be verified to fit the 64 MiB vendor_boot partition
before flashing.

## Sources

- TWRP device tree:
  https://github.com/JonesqPacMan/android_device_xiaomi_rothko_twrp
- Minimal TWRP AOSP manifest:
  https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp
