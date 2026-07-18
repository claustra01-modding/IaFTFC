# IaFTFC 開発ガイド

## プロジェクトの目的

- Mod 名は `IaFTFC`、Mod ID は `iaftfc`、Java パッケージは `net.claustra01.iaftfc` とする。
- TerraFirmaCraft（TFC）の世界に Ice and Fire: Community Edition（IaF CE）のドラゴン関連構造物を自然生成する互換 Mod とする。
- TFC と IaF CE の既存コンテンツを尊重し、可能な限りデータ駆動のワールド生成で統合する。

## 現在の開発環境

- Minecraft: `1.21.1`
- Mod ローダー: NeoForge `21.1.235`
- Java: `21`
- ビルド: Gradle Wrapper（`./gradlew`）
- NeoForge MDK の雛形は IaFTFC 用の最小構成へ置き換え済みである。

バージョン番号は `gradle.properties` を正とし、この節と食い違う場合は同ファイルを確認して本書も更新すること。

## 実装方針

- Java ソースは `src/main/java/net/claustra01/iaftfc/` に置く。
- IaFTFC 固有リソースの名前空間は `iaftfc` とする。他 Mod のタグへ値を追加する互換データに限り、対象 Mod の名前空間（現在は `iceandfire`）へ `replace: false` のタグファイルを置く。
- サンプルの `com.example.examplemod`、`examplemod`、サンプルブロック／アイテム／設定は製品コードに残さない。
- TFC 4.x と IaF CE 2.x は必須依存関係として Mod メタデータに明記する。
- 他 Mod の内部実装への依存は最小限にし、公開 API、レジストリ、タグ、JSON データを優先する。
- ドラゴン構造物は IaF CE の `iceandfire:structure_gen/fire`、`iceandfire:structure_gen/ice`、`iceandfire:structure_gen/lightning` バイオームタグへ、TFC が提供する NeoForge 共通気候タグを追加して有効化する。
- IaF CE 本体が構造物、ドラゴン、戦利品、生成間隔、生成確率を管理するため、IaFTFC 側で同じ構造物を複製しない。
- ワールド生成は、新規チャンクで決定的に動作し、既存チャンクを暗黙に変更しない設計にする。
- IaF CE の構造物 ID や TFC のバイオームタグは、対象バージョンの実物または公式ソースで確認してから固定する。
- クライアント専用クラスを共通／サーバー側から参照しない。専用サーバーでのロードを必ず考慮する。

## 検証

変更内容に応じて、少なくとも次を実行する。

```sh
./gradlew compileJava
./gradlew build
```

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
- TFC 4.x と IaF CE 2.x は `neoforge.mods.toml` で必須依存関係として設定済みである。実装はデータ駆動で両 Mod の Java API を参照しないため、コンパイル用 JAR は不要である。
- 暑い TFC バイオームへファイアドラゴン、寒い TFC バイオームへアイスドラゴン、湿潤な TFC バイオームへライトニングドラゴンの巣と洞窟を追加するタグ統合は実装済みである。
- `./gradlew compileJava` と `./gradlew build` は成功している。
- TFC と IaF CE を導入した新規ワールドでの実生成確認は未実施である。
