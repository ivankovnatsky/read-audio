{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/229bce01ddf60809aaafbead216bae561dd52c55";
    flake-utils.url = "github:numtide/flake-utils/11707dc2f618dd54ca8739b309ec4fc024de578b";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
      in
      {
        packages = {
          video-summarizer = mkPoetryApplication {
            projectDir = ./.;
            preferWheels = true;

            # Runtime dependencies
            propagatedBuildInputs = with pkgs; [
              ffmpeg
              ollama
            ];
          };
          default = self.packages.${system}.video-summarizer;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
            poetry
            ffmpeg
            ollama
            ruff
            llvmPackages_14.llvm
            pkg-config
            gcc
            daemon
            yt-dlp
          ];

          # Set environment variables for llvmlite and ensure Ollama model is available
          shellHook = ''
            export LLVM_CONFIG=${pkgs.llvmPackages_14.llvm}/bin/llvm-config
            export LDFLAGS="-L${pkgs.llvmPackages_14.llvm}/lib"
            export CPPFLAGS="-I${pkgs.llvmPackages_14.llvm}/include"

            # Start Ollama service if not running
            if ! pgrep -f "${pkgs.ollama}/bin/ollama serve" > /dev/null 2>&1; then
              ${pkgs.daemon}/bin/daemon \
                --name=ollama \
                --pidfile=/tmp/ollama.pid \
                --output=/tmp/ollama.log \
                --command="${pkgs.ollama}/bin/ollama serve"
              
              # Wait for service to start
              for i in {1..5}; do
                if curl -s http://localhost:11434/api/version >/dev/null 2>&1; then
                  break
                fi
                sleep 1
              done
            fi

            # Pull model in background if needed
            if ! ${pkgs.ollama}/bin/ollama list 2>/dev/null | grep -q "llama3.1:8b"; then
              (${pkgs.ollama}/bin/ollama pull llama3.1:8b > /dev/null 2>&1) &
              disown
            fi
          '';
        };
      });
}
