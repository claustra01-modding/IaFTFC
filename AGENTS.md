# IaFTFC 開発ガイド

## プロジェクトの目的

- Mod 名は `IaFTFC`、Mod ID は `iaftfc`、Java パッケージは `net.claustra01.iaftfc` とする。
- TerraFirmaCraft（TFC）の世界に Ice and Fire: Community Edition（IaF CE）のドラゴン関連構造物を自然生成し、3属性のドラゴンスチールをTFC金属加工へ統合する互換 Mod とする。
- TFC と IaF CE の既存コンテンツを尊重し、可能な限りデータ駆動のワールド生成で統合する。

## 現在の開発環境

- Minecraft: `1.21.1`
- Mod ローダー: NeoForge `21.1.235`
- Java: `21`
- ビルド: Gradle Wrapper（`./gradlew`）
- NeoForge MDK の雛形は IaFTFC 用の最小構成へ置き換え済みである。
- コンパイル時は Modrinth Maven の TerraFirmaCraft `4.2.5` APIを使用する。IaF CEとの連携はレジストリID、JSON、対象を限定したMixinで行い、IaF CE JARはコンパイル依存にしない。

バージョン番号は `gradle.properties` を正とし、この節と食い違う場合は同ファイルを確認して本書も更新すること。

IaFTFC の `mod_version` は常に `0.0.1` で固定し、機能追加や修正の際にも変更しない。

## 実装方針

- Java ソースは `src/main/java/net/claustra01/iaftfc/` に置く。
- IaFTFC 固有リソースの名前空間は `iaftfc` とする。他 Mod のタグへ値を追加する互換データに限り、対象 Mod の名前空間（現在は `iceandfire`）へ `replace: false` のタグファイルを置く。
- サンプルの `com.example.examplemod`、`examplemod`、サンプルブロック／アイテム／設定は製品コードに残さない。
- TFC 4.2.5 以上と IaF CE 2.x は必須依存関係として Mod メタデータに明記する。
- 他 Mod の内部実装への依存は最小限にし、公開 API、レジストリ、タグ、JSON データを優先する。
- ドラゴン構造物は IaF CE の `iceandfire:structure_gen/fire`、`iceandfire:structure_gen/ice`、`iceandfire:structure_gen/lightning` バイオームタグへ、`#iaftfc:dragon_structure_land` を追加して TFC の主要な陸上地形で有効化する。
- TFC のバイオーム ID は地形分類であって実気候ではないため、属性の選別にバイオーム名を使わない。
- IaF CE の巣・洞窟の構造物セットを属性別に分割し、TFC 4.2.5 の `tfc:climate` 配置でファイアは平均気温15℃以上かつ地下水量300未満、アイスは平均気温5℃以下、ライトニングは平均気温5℃超かつ地下水量300以上に制限する。属性間の配置条件は重複させない。
- 構造物セットの配置間隔は巣24チャンク、洞窟30チャンクとし、IaF CE の既定値（15、18チャンク）より低密度にする。全属性で村の構造物セットから10チャンクの除外距離を設ける。
- IaF CE 本体が構造物、ドラゴン、戦利品、各構造物内部の生成確率を管理するため、IaFTFC 側で同じ構造物を複製しない。
- IaF CEの巣と洞窟はJavaコードで直接生成されるため、対象pieceのチェスト配置だけをMixinで置換する。FireはTFC Chestnut、IceはWhite Cedar、LightningはBlackwoodのチェストを使用し、元のIaF CE loot tableは維持する。
- IaF CEのgold／silver／copper pileは元のlayers別ドロップ数を維持し、対応するTFCのnative gold／silver／copper powderをドロップするloot tableで上書きする。
- スポーン地点周辺の生成禁止距離は IaF CE の `dangerousDistanceLimit`（既定値 1000 ブロック）をそのまま使用し、IaFTFC 側では上書きしない。
- ワールド生成は、新規チャンクで決定的に動作し、既存チャンクを暗黙に変更しない設計にする。
- IaF CE の構造物 ID や TFC のバイオームタグは、対象バージョンの実物または公式ソースで確認してから固定する。
- クライアント専用クラスを共通／サーバー側から参照しない。専用サーバーでのロードを必ず考慮する。

## ドラゴンスチール統合

- `dragonsteel_fire`、`dragonsteel_ice`、`dragonsteel_lightning`をTFCの`RegistryMetal`として登録する。基準素材は順にRed Steel、Blue Steel、Black Steelとする。
- IaFTFC側のインゴットを正規の加工素材とし、IaF CE既存インゴットも共通インゴットタグへ含める。完成品のtool／armorはIaF CE既存アイテムを維持する。
- 各金属にingot、double ingot、sheet、double sheet、rod、sword blade、4種のunfinished armor、block、slab、stairs、anvil、molten fluidを実装する。sword以外のtool headは追加しない。
- Dragon Forgeの入力はFire=`#c:ingots/red_steel`、Ice=`#c:ingots/blue_steel`、Lightning=`#c:ingots/black_steel`とし、特定のTFCアイテムIDへ固定しない。出力はIaFTFCの対応インゴットとする。
- Dragon Forgeで完成したIaFTFCドラゴンスチールインゴットには、完成時点でTFCの温度1600℃を付与する。レシピ読込時ではなく出力スロットへ配置された直後に温度を設定する。
- IaF CE既存swordレシピはTFC式のsword bladeと木のrodの組み立てへ置換し、鍛造ボーナスを引き継ぐ。axe、hoe、pickaxe、shovelは同名レシピを無効化し、IaFTFCでは製作対応しない。armorレシピはunfinished armorとsheet類の溶接へ置換する。
- ドラゴンスチール金床はTFC Red／Blue Steelより1段階高いtier 7とする。導入経路を閉じないためdouble ingotの最初の溶接だけtier 6で行い、金床製作後のsheet、rod、sword blade、unfinished armor、double sheet、完成armorはtier 7を要求する。
- 3属性共通で溶融温度は2000℃、鍛造可能温度は1200℃、溶接可能温度は1600℃とし、TFC最高級鋼より明確に高温を要求する。
- 表示言語は`en_us`のみを同梱し、`ja_jp`は追加しない。
- テクスチャとJSONは`tools/regenerate_dragonsteel.py`を正とする。通常の金属形状はTFCの形状とIaF CEの各属性インゴット配色から輝度パレット転写で生成し、unfinished armorはIaF CEの対応する完成防具テクスチャを彩度55%へ落として使用する。手編集との二重管理を避ける。再生成にはPython 3、Pillow、対象バージョンのTFC／IaF CE JARが必要である。
- 金属block、slab、stairsの英語表示名はTFCに合わせて`Plated Block`、`Plated Slab`、`Plated Stairs`とする。
- IaFTFCの金床はNeoForgeの`BlockEntityTypeAddBlocksEvent`でTFCの`ANVIL` BlockEntityTypeへ追加する。TFCの`AnvilBlock`だけを生成してBlockEntityTypeの有効ブロック登録を省略してはならない。

## 検証

変更内容に応じて、少なくとも次を実行する。

```sh
./gradlew compileJava
./gradlew build
```

データを変更した場合は、全JSONが構文解析できることと、生成物のPNGが16x16 RGBAであることも確認する。開発用クライアント／サーバーの起動は、ユーザーから明示的に依頼された場合だけ行う。

ワールド生成を変更した場合は、可能なら開発用サーバーまたは GameTest で次も確認する。

- TFC ワールドの新規チャンクで対象構造物が生成される。
- 構造物が不適切なバイオーム、海上、空中などに生成されない。
- 同じシードで配置が再現される。
- TFC または IaF CE が不足している場合、依存関係エラーが明確に表示される。

## AGENTS.md の保守ルール

- このファイルは常に現在のリポジトリ状態を表すこと。
- パッケージ、Mod ID、対応バージョン、依存関係、ディレクトリ構成、ビルド／検証手順、実装方針を変更した場合は、同じ作業内で本書も更新する。
- 完了済みの内容を「予定」として残さず、未実装の内容を「実装済み」と書かない。
- 一時的な調査メモや推測は記載せず、確認できた事実と継続的に有効なルールだけを残す。
- 作業開始時と終了前に本書を読み、実装との差分がないか確認する。

## 現在の作業状況

- Mod ID `iaftfc`、パッケージ `net.claustra01.iaftfc` への置き換えは完了している。
- TFC 4.2.5 以上と IaF CE 2.x は `neoforge.mods.toml` で必須依存関係として設定済みである。TFC APIはコンパイル時に使用し、IaF CE連携はJSON、レジストリID、対象限定Mixinで構成している。
- Mod バージョンは固定値 `0.0.1` である。
- 主要な TFC 陸上バイオームを全属性のドラゴン構造物タグへ追加する統合は実装済みである。
- ファイア、アイス、ライトニングの巣と洞窟を別々の `tfc:climate` 構造物セットへ分割し、重複しない実気温・地下水量条件で生成を制限済みである。配置間隔は IaF CE の既定値より広く、全属性へ村からの除外距離を設定している。
- エントリーポイントは初期化だけを担当し、ワールド生成のキーと診断処理は `worldgen/DragonWorldgen.java` に集約している。
- サーバー起動時に、共通陸上タグ、属性別タグ、6つの気候構造物セットを一括検証する診断処理を実装済みである。
- 3属性のドラゴンスチール金属、tier 7金床、加工途中品、溶融流体、TFC式sword／armorレシピ、非対応toolレシピの無効化、Dragon Forge素材タグ置換を実装済みである。
- 3属性の巣・洞窟チェストを属性別TFC木材へ置換し、3種のmetal pileをTFC native metal powderドロップへ置換済みである。
- Dragon ForgeのIaFTFCインゴット出力へ、精錬完了時に1600℃を付与する処理を実装済みである。
- 3属性の金床はTFCのAnvilBlockEntityに有効なブロックとして登録済みであり、設置時の`Invalid block entity tfc:anvil`クラッシュを修正済みである。
- TFCおよびIaF CEの既存テクスチャを基に、全金属形状のテクスチャを再現可能な生成スクリプトと生成済みリソースを実装済みである。
- `./gradlew build`、全JSONの構文解析、全PNGの16x16 RGBA検証は成功している。
- TFC 4.2.5 と IaF CE 2.0 を導入した環境でドラゴン構造物の生成は確認済みである。実気候による属性分離は未確認である。
