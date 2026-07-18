# IaFTFC

Minecraft 1.21.1／NeoForge 向けの TerraFirmaCraft と Ice and Fire: Community Edition の互換 Mod です。

TFC の主要な陸上バイオームを Ice and Fire CE のドラゴン構造物タグへ追加し、TFC の実気候に応じて新規チャンクに次の構造物を生成します。

- 平均気温15℃以上かつ地下水量300未満: ファイアドラゴンの巣、洞窟
- 平均気温5℃以下: アイスドラゴンの巣、洞窟
- 平均気温5℃超かつ地下水量300以上: ライトニングドラゴンの巣、洞窟

属性同士の配置条件は重ならず、配置間隔は巣が24チャンク、洞窟が30チャンクです。これは Ice and Fire CE の既定値（15、18チャンク）より低密度です。構造物本体、ドラゴン、戦利品、各構造物内部の生成確率は Ice and Fire CE の実装と設定を使用します。既存チャンクへ構造物を後から追加する機能はありません。

スポーン地点周辺の生成禁止距離も Ice and Fire CE の `dangerousDistanceLimit`（既定値 1000 ブロック）を使用します。

## ドラゴンスチール

Fire、Ice、Lightning DragonsteelをTFC金属として追加します。各属性にインゴット、ダブルインゴット、板、ダブル板、棒、sword blade、unfinished armor、金属ブロック類、溶融流体、Red／Blue Steelより1段階高いtier 7金床があります。

金属ブロック類はTFCと同じ`Plated Block`／`Plated Slab`／`Plated Stairs`表記です。3属性とも鍛造1200℃、溶接1600℃、融点2000℃の高温加工を要求します。

Dragon Forgeで鉄の代わりに次のTFC鋼を使用します。

- Fire Dragonsteel: `#c:ingots/red_steel`
- Ice Dragonsteel: `#c:ingots/blue_steel`
- Lightning Dragonsteel: `#c:ingots/black_steel`

完成swordは鍛造したbladeと木のrodから組み立て、完成armorはunfinished armorと板類をtier 7金床で溶接します。axe、hoe、pickaxe、shovelのレシピは削除され、IaFTFCでは対応しません。完成品そのものはIce and Fire CEの既存Dragonsteel sword／armorです。

## 生成確認

構造物は新規生成チャンクだけが対象です。既存ワールドで確認する場合は、まだ探索していない場所へ移動してください。

サーバー起動時に、陸上バイオームタグ、属性別タグ、6つの気候構造物セットを検証します。すべて正常なら次の形式で出力されます。

```text
IaFTFC world generation ready: ... TFC land biomes and 6 climate-filtered dragon structure sets
```

代わりに `ERROR` が出た場合は、TFC または Ice and Fire CE のバージョンと `latest.log` を確認してください。

TFC のバイオーム ID は地形を表し、気温や地下水量は座標ごとに別管理されます。IaFTFC は TFC 4.2.5 の `tfc:climate` 構造物配置を使用して、実際の気候データでドラゴン属性を選別します。

## 必須 Mod

- TerraFirmaCraft 4.2.5 以上
- Ice and Fire: Community Edition 2.x
- 上記 Mod が要求する依存 Mod

## ビルド

Java 21 を使用します。

```sh
./gradlew build
```

生成物は `build/libs/iaftfc-0.0.1.jar` です。Modバージョンは常に`0.0.1`で固定します。

DragonsteelのJSONとテクスチャは`tools/regenerate_dragonsteel.py`で再生成できます。Python 3、Pillow、TFC 4.2.5とIaF CE 2.0のJARを指定してください。
