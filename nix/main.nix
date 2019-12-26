let
  duplKey = builtins.readFile ../secrets/pydriveprivatekey.pem;
  dbPath = "/opt/plugserv/plugserv_db.sqlite3";
in let
  genericConf = { config, pkgs, ... }: {
    virtualisation.docker = {
      enable = true;
      logDriver = "journald";
    };
    docker-containers.plugserv = {
      image = "plugserv:latest";
      ports = [ "127.0.0.1:8000:8000" ];
      volumes = [ "/opt/plugserv:/opt/plugserv" ];
    };

    services.nginx = {
      enable = true;
      recommendedGzipSettings = true;
      recommendedOptimisation = true;
      recommendedProxySettings = true;
      recommendedTlsSettings = true;
      upstreams.gunicorn = {
        servers = {
          "127.0.0.1:8000" = {};
        };
      };
      virtualHosts."www.plugserv.com" = {
        enableACME = true;
        forceSSL = true;
        locations."/assets/" = {
          alias = "/opt/plugserv/assets/";
        };
        locations."/" = {
          proxyPass = "http://gunicorn";
        };
      };
      # reject requests with bad host headers
      virtualHosts."_" = {
        onlySSL = true;
        default = true;
        sslCertificate = ./fake-cert.pem;
        sslCertificateKey = ./fake-key.pem;
        extraConfig = "return 444;";
      };
      appendHttpConfig = ''
        error_log stderr;
        access_log syslog:server=unix:/dev/log combined;
      '';
    };
    services.journalbeat = {
      enable = true;
      extraConfig = ''
        journalbeat.inputs:
        - paths: ["/var/log/journal"]
          include_matches:
            - "UNIT=acme-www.plugserv.com.service"
            - "UNIT=duplicity.service"
            - "UNIT=docker-plugserv.service"
            - "_SYSTEMD_UNIT=nginx.service"
            - "_SYSTEMD_UNIT=docker-plugserv.service"
            - "_SYSTEMD_UNIT=sshd.service"
        output:
         elasticsearch:
           hosts: ["https://cloud.humio.com:443/api/v1/ingest/elastic-bulk"]
           username: anything
           password: ${builtins.readFile ../secrets/humiocloud.password}
           compression_level: 5
           bulk_max_size: 200
           worker: 1
           template.enabled: false
      '';
    };
    services.duplicity = {
      enable = true;
      root = "/tmp/db.backup";
      targetUrl = "pydrive://duply-alpha@repominder.iam.gserviceaccount.com/plugserv_backups/db3";
      secretFile = pkgs.writeText "dupl.env" ''
        GOOGLE_DRIVE_ACCOUNT_KEY="${duplKey}"
      '';
      extraFlags = ["--no-encryption"];
    };
    systemd.services.duplicity = {
      path = [ pkgs.bash pkgs.sqlite ];
      preStart = ''sqlite3 ${dbPath} ".backup /tmp/db.backup"'';
      # privateTmp should handle this, but this helps in case it's eg disabled upstream
      postStop = "rm /tmp/db.backup";
    };
    users = {
      # using another user for admin tasks would be preferable, but nixops requires root ssh anyway:
      # https://github.com/NixOS/nixops/issues/730
      users.root.extraGroups = [ "docker" ];
      users.root.openssh.authorizedKeys.keyFiles = [ ../../.ssh/id_rsa.pub ];
      users.plugserv = {
        group = "plugserv";
        isSystemUser = true;
        uid = 497;
      };
      groups.plugserv ={
        members = [ "plugserv" "nginx" ];
        gid = 499;
      };
    };

    networking.firewall.allowedTCPPorts = [ 22 80 443 ];

    nixpkgs.config = {
      allowUnfree = true;
    };
    nixpkgs.overlays = [ (self: super: {
      duplicity = super.duplicity.overrideAttrs (oldAttrs: { 
        doCheck = false;
        doInstallCheck = false;
      });
    }
    )];

    environment.systemPackages = with pkgs; [
      curl
      sqlite
      duplicity
      vim
      python3  # for ansible
    ];
  };
in {
  network.description = "plugserv";
  network.enableRollback = true;
  virtualbox = genericConf;
  alpha-simon-codes = genericConf;
}
