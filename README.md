# IaFTFC

Minecraft 1.21.1／NeoForge 向けの TerraFirmaCraft と Ice and Fire: Community Edition の互換 Mod です。

TFC が提供する共通バイオームタグを Ice and Fire CE のドラゴン構造物タグへ追加し、TFC 世界の新規チャンクに次の構造物を生成できるようにします。

- 暑い地域: ファイアドラゴンの巣、洞窟
- 寒い地域: アイスドラゴンの巣、洞窟
- 湿潤地域: ライトニングドラゴンの巣、洞窟

構造物本体、ドラゴン、戦利品、生成間隔、生成確率は Ice and Fire CE の実装と設定を使用します。既存チャンクへ構造物を後から追加する機能はありません。

## 必須 Mod

- TerraFirmaCraft 4.x
- Ice and Fire: Community Edition 2.x
- 上記 Mod が要求する依存 Mod

## ビルド

Java 21 を使用します。

```sh
./gradlew build
```

生成物は `build/libs/iaftfc-1.0.0.jar` です。
