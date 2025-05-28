cat << 'EOF' > docs/ARCH.md
```plantuml
@startuml
skinparam packageStyle rectangle

package "CLI" {
  [cli.py]
}
package "Container" {
  [pack.py]
  [unpack.py]
  [metadata.py]
}
package "Crypto" {
  [aead.py]
  [g_new.py]
  [kdf.py]
  [signature.py]
}
package "VDF" {
  [vdf.py]
  [phase_vdf.py]
}
package "Utils" {
  [constants.py]
  [formats.py]
  [logging.py]
}

' зависимости
cli.py --> pack.py
cli.py --> unpack.py
pack.py --> aead.py
pack.py --> kdf.py
unpack.py --> aead.py
metadata.py --> formats.py
g_new.py --> kdf.py
vdf.py --> logging.py
@enduml
