class Zilant < Formula
  desc "Zilant Prime Core"
  homepage "https://github.com/QuantumKeyUYU/zilant-prime-core"
  url "https://github.com/QuantumKeyUYU/zilant-prime-core/archive/v0.1.0.tar.gz"
  sha256 "0" # placeholder
  version "0.1.0"

  def install
    libexec.install Dir["*"]
    bin.install_symlink libexec/"start_zilant.ps1" => "zilant"
  end
end
