{
  virtualbox =
    { config, pkgs, ... }:
    { deployment.targetEnv = "virtualbox";
      deployment.virtualbox.memorySize = 1024; # megabytes
      deployment.virtualbox.vcpu = 2; # number of cpus
      deployment.virtualbox.headless = true;
    };
  alpha-simon-codes =
    { config, lib, pkgs, ... }:
    { deployment.targetHost = "alpha.simon.codes";
      networking.hostName = "alpha.simon.codes";

      # from generated configuration.nix
      boot.loader.grub.device = "/dev/vda";
      boot.loader.grub.enable = true;
      boot.loader.grub.version = 2;
      services.openssh.enable = true;
      services.openssh.permitRootLogin = "prohibit-password";
      system.stateVersion = "18.09";

      # from generated hardware-configuration.nix
      boot.initrd.availableKernelModules = [ "ata_piix" "uhci_hcd" "virtio_pci" "sr_mod" "virtio_blk" ];
      boot.kernelModules = [ ];
      boot.extraModulePackages = [ ];

      fileSystems."/" =
        { device = "/dev/disk/by-uuid/25cf9a34-5406-44ad-8ec0-dab5cf7e5a25";
          fsType = "ext4";
        };

      swapDevices =
        [ { device = "/dev/disk/by-uuid/889d437f-e6ca-4c53-964d-963ee26d72c7"; }
        ];

      nix.maxJobs = lib.mkDefault 1;
      virtualisation.hypervGuest.enable = false;
    };
}
