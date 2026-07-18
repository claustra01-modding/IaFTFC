# IaFTFC 開発ガイド

## プロジェクトの目的

- Mod 名は `IaFTFC`、Mod ID は `iaftfc`、Java パッケージは `net.claustra01.iaftfc` とする。
- TerraFirmaCraft（TFC）の世界に Ice and Fire: Community Edition（IaF CE）のドラゴン関連構造物を自然生成し、ドラゴンスチール、食料、ドラゴンの餌をTFCの仕組みへ統合する互換 Mod とする。
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
- IaF CEの巣と洞窟はJavaコードで直接生成されるため、対象pieceのチェスト配置だけをMixinで置換する。FireはTFC Chestnut、IceはWhite Cedar、LightningはBlackwoodのチェストを使用する。
- 9種のドラゴンチェストloot tableは[共通再設計仕様](https://gist.github.com/claustra01/0b96699ab853bc17da8384426c6ffe5b)を正とし、元IaF CE tableのpool、rolls、entry数、weight、count、conditions、IaF固有品を維持したカテゴリ変換として生成する。Roostはordinary、Female Caveはdangerous、Male Caveはlategameとする。
- 汎用gemは`shared/gems`、汎用iron等のingotはprofile別`shared/ingots`へ送り、属性entryだけFire ruby／gold、Ice sapphire／silver、Lightning topaz／copperへ固定する。nuggetは同じ個数の対応small native oreへ変換する。個数範囲をIaFTFC側で再調整しない。
- ドラゴンチェストlootのVanilla Chainは、元entryのweight、count、conditionsを維持して`tfc:metal/chain/wrought_iron`へ置換する。
- 装備entryはsword、helmet、chestplate、greaves、bootsを個別のprofile別shared tableへ送る。ordinary装備はcopper／bronze／bismuth bronze／black bronze、dangerous装備はwrought iron、lategame装備はsteelのみとし、加工途中品:完成品のweight合計を2:1にする。元のenchantmentは完成品branchだけへ移す。black steelはlategame汎用ingotだけに許可し、black steel装備およびred／blue steelの汎用lootは禁止する。
- IaF CEのgold／silver／copper pileは対応するTFCのsmall native gold／silver／copper oreをドロップするloot tableで上書きし、layers 1～8の個数は順に1～8個（IaF CE元ドロップの半量）とする。
- IaF CEのドラゴン洞窟鉱石は、配置地点周辺のTFC岩石種を参照したTFC鉱石へ置換する。commonはrich native copper／malachite／tetrahedrite／hematite／magnetite／limonite、uncommonはrich cassiterite／bismuthinite／sphalerite、rareはrich native gold／native silver／garnierite、属性固有はFire=ruby、Ice=sapphire、Lightning=topazとする。
- TFC側の銀・サファイア体系を正規経路とするため、IaF CEのsilver ingot／nugget／block／raw silverの精錬・圧縮、silver tool／metal armor／pile、sapphire ore精錬・gem／block変換レシピを無効化する。構造物に生成される`silver_pile`ブロック自体は有効なIaF CE固有ブロックとして維持し、`[DISABLED]`は表示しない。`dragonscales_silver`／`dragonscales_sapphire`は金属・宝石ではなくドラゴン鱗の色名なので対象外とする。
- レシピを無効化したIaF CEのsilver／sapphire素材、鉱石、加工品、metal tool／armor、非Iron・非Dragonsteelの既存ドラゴン防具、3属性のDragonsteel axe／hoe／pickaxe／shovel、およびIaF CE既存Dragonsteel Ingot／Block各3種には、クライアントtooltip末尾へ赤色の`[DISABLED]`を表示する。`silver_pile`と色名としてのdragon scale系には表示しない。
- IaF CEのブレス地形変換へ、TFCのgrass、dirt、coarse dirt、rooted dirt、mud、farmland、grass path、raw／hardened rock、cobble／mossy cobble、rock gravelを追加する。TFC由来の変換結果は`revert=false`として岩石種・土壌種をVanillaブロックへ失わないようにする。階段、slab、wall、装置、金属は一律変換しない。TFCのlogs、planks、leaves、cropsは標準ブロックタグ経由でIaF CE本来の処理を使う。
- IaF CE本体でプレイヤーが摂取可能なドラゴン肉3種、Pixie Dust、Ambrosia、Cannoli、ドラゴン肉入り炒飯3種、Ghost Cream、Pixie Dust Milky Teaの11品へ、TFC食料定義と`#c:foods`分類を追加する。栄養カテゴリと腐敗速度はTFC 4.2.5の実データを基準にし、満腹度と特殊食品としての強さはVanilla／IaF CE本来の値を維持する。ドラゴン肉とドラゴン肉料理は通常のTFC食料より高栄養でよく、CannoliなどIaF CE側で意図的に強力な食品も一律に弱体化しない。
- Fire／Frost／Lightning StewはIaF CE本体ではfood componentを持たないドラゴン繁殖専用アイテムであるため、TFC食料化せず、プレイヤーが摂取可能になるJava変更も加えない。
- TFCの`#c:foods/meat`を`#minecraft:meat`およびIaF CEの`dragon_food_meat`へ追加し、TFCの生肉と加熱肉をドラゴンの手渡し・落下アイテムによる給餌へ対応させる。ドラゴン繁殖はIaF CE本来の属性シチュー専用条件を維持し、通常の肉では繁殖させない。
- IaF CEドラゴンの手渡し給餌と落下食材を探すAIの両方で、TFCの`FoodCapability.isRotten`が真の食材を拒否する。落下食材は探索開始後に腐敗した場合も接触時に消費せず、IaF CE本来の非腐敗食材と繁殖専用シチューの挙動は変更しない。
- IaF CEのItem Size／Weightは、TFC 4.2.5の`item_size`実データと`ItemSizeManager`のfallback値を基準に、IaF CE 2.0 JAR内の全item modelを重複なくカテゴリ分類して定義する。標準的なblock、food、plant、stair、slab、log、chest、ingot、ore、bottle、tool、armor等は対応するTFCカテゴリと同値にし、用途や形状が異なるアイテムを名前だけで一括推測しない。
- Item Size／Weightの確定済み例外はDragon Egg=`very_large`／`very_heavy`、Dragon Skull=`huge`／`very_heavy`とする。プレイヤー装備のDragonsteel ArmorはTFCのarmor既定値に合わせて`large`／`very_heavy`、IaF CE既存品とIaFTFC独自品のドラゴン用Dragon Armorは`very_large`／`very_heavy`とする。Dragon Forgeのbrick／core／inputは特殊設備扱いせず、すべて一般BlockItemと同じ`small`／`light`とする。
- ブレス変換先のIaF CEブロックはTFCの同系統地形挙動へ合わせる。3属性のstoneはcollapse／start collapse／trigger collapse、cobblestoneとgravelはlandslide、dirt pathはlandslide支持ブロックへ追加する。IaF CEのgravel変換先は本体の`FallingReturningStateBlock`による重力落下も維持する。通常dirt／grassはTFCの同名系統と同様にこれらのタグへ追加しない。
- IaF CEの物理武器にはTFCの斬撃／刺突／打撃item tagを形状に応じて付与する。sword／axe／hoe／macuahuitlは斬撃、bow／dagger／pickaxe／spear／tridentは刺突、shovel／gauntlet／slapper／troll weaponは打撃とする。IaF CE本体の攻撃力や特殊効果は上書きしない。
- Dragon Scale Armor全12色はTFC Leather Armorと同じ部位別knapping patternで製作する。全色共通のknapping typeと色別recipe ingredientを使用し、対応色以外のScaleでは完成しないままJEIでは1つのDragon Scale knappingタブへ統合する。Helmet／Chestplate／Leggings／Bootsのどの部位でも完成時にScale 5枚を消費し、IaF CE既存の作業台レシピは同一recipe IDのknappingレシピで置換する。
- IaF CE防具のTFC物理耐性は本体の防御段階に対応するTFC 4.2.5実値を使用する。Copper MetalはCopper、Silver MetalはBronze、Death Worm／TrollはWrought Iron、Dragon Scale／Sea SerpentはBlack Steel、Dragonsteelは全物理耐性75とする。Sheep／Blindfold／EarplugsはLeather、Hippogryph ArmorとDragon Armorは素材に対応するTFC金属値を使用する。IaFTFC独自Dragon Armor 4系統にも対応するSteel／Black Steel／Red Steel／Blue Steel値を付与する。
- Fire／Ice／Lightning DragonはIaF CE本体の高い体力・Armor・成長補正を尊重し、追加するTFC物理耐性は刺突／斬撃／打撃各30（各約25.9%軽減）に留める。TFC 4.2.5の動物には追加entity damage resistanceがないため、それらよりやや硬い程度の補正とする。近接攻撃の物理種別は斬撃とし、ブレスや属性攻撃についてDamage Type側で物理種別が確定している場合はその種別を優先する。
- スポーン地点周辺の生成禁止距離は IaF CE の `dangerousDistanceLimit`（既定値 1000 ブロック）をそのまま使用し、IaFTFC 側では上書きしない。
- ワールド生成は、新規チャンクで決定的に動作し、既存チャンクを暗黙に変更しない設計にする。
- IaF CE の構造物 ID や TFC のバイオームタグは、対象バージョンの実物または公式ソースで確認してから固定する。
- クライアント専用クラスを共通／サーバー側から参照しない。専用サーバーでのロードを必ず考慮する。

## ドラゴンスチール統合

- `dragonsteel_fire`、`dragonsteel_ice`、`dragonsteel_lightning`をTFCの`RegistryMetal`として登録する。基準素材は順にRed Steel、Blue Steel、Black Steelとする。
- IaFTFC側のインゴットとPlated Blockだけを正規の加工素材とし、IaF CE既存Dragonsteel Ingot／Block各3種は無効化する。IaF CE既存Dragonsteel Blockからのクラフト分解とTFC溶解経路も無効化する。完成品のtool／armorはIaF CE既存アイテムを維持する。
- 各金属にingot、double ingot、sheet、double sheet、rod、sword blade、4種のunfinished armor、block、slab、stairs、anvil、molten fluidを実装する。sword以外のtool headは追加しない。
- Dragon Forgeの入力はFire=`#c:ingots/red_steel`、Ice=`#c:ingots/blue_steel`、Lightning=`#c:ingots/black_steel`とし、特定のTFCアイテムIDへ固定しない。出力はIaFTFCの対応インゴットとする。
- Dragon Forgeで完成したIaFTFCドラゴンスチールインゴットには、完成時点でTFCの温度1750℃を付与する。レシピ読込時ではなく出力スロットへ配置された直後に温度を設定する。
- IaF CE既存swordレシピはTFC式のsword bladeと木のrodの組み立てへ置換し、鍛造ボーナスを引き継ぐ。axe、hoe、pickaxe、shovelは同名レシピを無効化し、IaFTFCでは製作対応しない。armorレシピはunfinished armorとsheet類の溶接へ置換する。
- ドラゴン防具はSteel、Black Steel、Red Steel、Blue Steelの4系統を追加し、各系統にhead、neck、body、tailを登録する。防御値は順に3.5、5.5、7.5、7.5とし、IaF CE既存値を含めてIron < Steel < Black Steel < Red／Blue Steel < Dragonsteelとなるよう維持する。
- Iron、3属性Dragonsteel、新規4系統のドラゴン防具は元の部位別クラフト形状を維持し、素材を対応する`#c:double_sheets/*`へ置換する。Copper、Gold、Silver、Diamond、Netheriteの既存ドラゴン防具レシピは無効化し、アイテムへ赤い`[DISABLED]`ツールチップを付与する。
- ドラゴンスチール金床はTFC Red／Blue Steelより1段階高いtier 7とする。導入経路を閉じないためdouble ingotの最初の溶接だけtier 6で行い、金床製作後のsheet、rod、sword blade、unfinished armor、double sheet、完成armorはtier 7を要求する。
- 3属性共通で溶融温度は2000℃、鍛造可能温度は1200℃、溶接可能温度は1600℃とし、TFC最高級鋼より明確に高温を要求する。
- 表示言語は`en_us`のみを同梱し、`ja_jp`は追加しない。
- テクスチャとJSONは`tools/regenerate_dragonsteel.py`を正とする。通常の金属形状はTFCの形状とIaF CEの各属性インゴット配色から輝度パレット転写で生成し、unfinished armorはIaF CEの対応する完成防具テクスチャを彩度55%へ落として使用する。手編集との二重管理を避ける。再生成にはPython 3、Pillow、対象バージョンのTFC／IaF CE JARが必要である。
- 新規ドラゴン防具のレシピ、モデル、英語名、テクスチャ、Item Size／Weight定義は`tools/regenerate_dragon_armor.py`を正とする。テクスチャはIaF CE既存ドラゴン防具間で一致するサドル・革などの画素を維持し、地金部分だけをTFCの各double sheet配色へ変換する。エンティティ描画用テクスチャはIaF CEの描画規約に合わせて`assets/iceandfire/textures/entity/dragon_armor`へ配置する。
- ドラゴンチェストloot tableと全shared tableは`tools/regenerate_dragon_chest_loot.py`を正とし、IaF CE 2.0 JARとTFC 4.2.5 JARを入力して再生成する。生成器は元tableとの構造・count・weight比較、profile上限、装備比率、enchantment位置、禁止金属、graphite配置、TFC item IDを検証する。生成済みJSONを個別に手編集して二重管理しない。
- TFC側と競合するIaF CEの銀・サファイアレシピ無効化JSONは`tools/regenerate_disabled_iaf_recipes.py`を正とする。
- IaF CE食料のTFC食料定義とドラゴン用肉タグは`tools/regenerate_food_compat.py`を正とし、IaF CE 2.0 JARとTFC 4.2.5 JARを入力して再生成する。生成器はTFCの基準食料をJARから読み取り、対象アイテムの存在、TFC食料フィールド、栄養素、満腹度、腐敗速度を検証する。
- IaF CEアイテムのItem Size／Weight定義と分類タグは`tools/regenerate_iaf_item_sizes.py`を正とし、IaF CE 2.0 JARとTFC 4.2.5 JARを入力して再生成する。生成器はIaF CEのitem modelとblockstateを実物から列挙し、全モデルの一意な分類、TFC参照値、確定済み例外を検証する。生成済みJSONを個別に手編集しない。
- IaF CEの物理武器tag、防具耐性、ドラゴンの攻撃種別と耐性は`tools/regenerate_physical_damage.py`を正とし、IaF CE 2.0 JARとTFC 4.2.5 JARを入力して再生成する。生成器は対象item model、Dragon entityの実在、TFC防具耐性の実値、全対象の一意な物理種別を検証する。
- Dragon Scale Armorのknapping type、色別Scaleタグ、レシピ、盤面テクスチャ、JEIカテゴリ英語名は`tools/regenerate_dragon_scale_knapping.py`を正とし、IaF CE 2.0 JARとTFC 4.2.5 JARを入力して再生成する。生成器はTFC Leather Armorの部位別patternとIaF CE既存レシピのscale／resultを実物から検証し、TFCが入力item pathから参照する12色のGUIテクスチャへIaF CEの対応Dragon Scale Blockテクスチャを配置する。
- 金属block、slab、stairsの英語表示名はTFCに合わせて`Plated Block`、`Plated Slab`、`Plated Stairs`とする。
- Dragonsteel Plated BlockのItem Size／Weightは一般BlockItem相当の`small`／`light`、Plated SlabはTFC Slab相当の`small`／`very_light`、Plated StairsはTFC Stairs相当の`small`／`light`とする。Dragonsteel Anvilは`#tfc:anvils`を通じてTFC Anvil相当の`huge`／`very_heavy`とする。
- IaFTFCの金床はNeoForgeの`BlockEntityTypeAddBlocksEvent`でTFCの`ANVIL` BlockEntityTypeへ追加する。TFCの`AnvilBlock`だけを生成してBlockEntityTypeの有効ブロック登録を省略してはならない。
- 新規ドラゴン防具はIaF CEのスロット判定・防御計算・描画との互換性を保つため、登録時にIaF CEの`DragonArmorItem`を生成する。IaF CE内部クラスをコンパイル時APIとして直接参照せず、連携処理は`dragonarmor`パッケージへ集約する。

## 検証

変更内容に応じて、少なくとも次を実行する。

```sh
./gradlew compileJava
./gradlew build
```

データを変更した場合は全JSONを構文解析する。生成物のPNGはitem textureが16x16 RGBA、ドラゴン防具のentity textureが512x256 RGBAであることも確認する。開発用クライアント／サーバーの起動は、ユーザーから明示的に依頼された場合だけ行う。

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
- 3属性の巣・洞窟チェストを属性別TFC木材へ置換し、9種のチェストlootをordinary／dangerous／lategame profileによるTFCカテゴリ変換へ移行済みである。元tableの報酬量とentry weightを維持し、Vanilla ChainはWrought Iron Chainへ、装備は加工途中品2:完成品1へ置換し、Male Caveのenchantmentはsteel完成品だけへ適用する。3種のmetal pileは元の半量のTFC small native metal oreドロップへ置換済みである。
- IaF CEの銀・サファイアについて、TFC側と競合する精錬、素材圧縮、tool、metal armor、pile、gem／block変換の28レシピを無効化済みである。構造物に生成されるSilver Pileブロック本体と色名としてのsilver／sapphire dragon scale系は維持するが、Silver PileのクラフトレシピとSilver Dragon Armorを含む非Iron・非Dragonsteelの既存ドラゴン防具レシピは無効化済みである。
- Steel、Black Steel、Red Steel、Blue Steelのドラゴン防具16点と、Iron／Dragonsteelを含むdouble sheet式レシピを実装済みである。Copper、Gold、Silver、Diamond、Netheriteのドラゴン防具20点には`[DISABLED]`表示を実装済みである。
- 無効化対象のIaF CE silver／sapphire系19アイテム、IaF CE既存Dragonsteel Ingot／Block各3アイテム、非対応Dragonsteel tool 12アイテム、非Iron・非Dragonsteelの既存ドラゴン防具20アイテムへ、赤色の`[DISABLED]`tooltipを追加済みである。Silver Pileには表示しない。
- ドラゴン洞窟内のcommon／uncommon／rare／属性固有鉱石を、配置地点周辺のTFC岩石種に合う指定TFC鉱石へ置換済みである。金属鉱石はすべてrich品位とする。
- Dragon ForgeのIaFTFCインゴット出力へ、精錬完了時に1750℃を付与する処理を実装済みである。
- ドラゴンブレスによるTFC自然地形のCharred／Frozen／Crackled変換を実装済みである。TFC由来の変換ブロックは永続し、IaF CEの固定Vanilla復元先へ戻さない。
- IaF CE本体で摂取可能な食用アイテム11種へ、IaF CE本来の強さとTFC 4.2.5の栄養・腐敗尺度を両立した食料定義を追加済みである。属性シチュー3種は繁殖専用の非食用アイテムとして維持する。TFCの生肉・加熱肉はIaF CEドラゴンの給餌に使用できるが、繁殖には従来どおり対応属性のシチューを要求する。
- IaF CEドラゴンは、TFCで腐敗済みと判定された肉・食材を手渡しでも落下アイテムでも食べない。落下食材が探索中に腐敗した場合も消費しない。
- IaF CE 2.0の全item model 528件をTFC 4.2.5の実データに対応するItem Size／Weightカテゴリへ分類し、データ定義を追加済みである。Dragon EggとDragon Skullは確定済みの例外値を使用し、プレイヤー用Dragonsteel Armorとドラゴン用Dragon Armorは別カテゴリで定義している。Dragon Forge全構成ブロックは一般BlockItem相当であり、IaFTFC独自Dragon Armor 16点にも既存Dragon Armorと同じ定義を追加済みである。
- IaF CEの武器model 60件へTFC物理攻撃種別、IaF CEおよびIaFTFCの防具182点へTFC物理耐性、3属性Dragonへ斬撃攻撃種別と全物理耐性30を設定済みである。Dragon Scale／Sea SerpentはBlack Steel相当、Dragonsteelは全物理耐性75とする。
- Dragon Scale全12色共通のknapping typeと色別ingredient、TFC Leather Armor patternを使用するArmor 4部位計48レシピを実装済みである。全部位のScale消費数は5枚で、元の作業台レシピは置換済みである。対応Dragon Scale Blockを使用した12色の盤面テクスチャを同梱し、JEI表示は英語名`Dragon Scale Knapping Recipe`の1タブに統合している。
- 3属性のブレス変換先stone／cobblestone／gravel／dirt pathへTFCのcollapse／landslide関連タグを追加済みであり、gravelはIaF CE本体のfalling block実装も維持している。
- 3属性の金床はTFCのAnvilBlockEntityに有効なブロックとして登録済みであり、設置時の`Invalid block entity tfc:anvil`クラッシュを修正済みである。
- TFCおよびIaF CEの既存テクスチャを基に、全金属形状のテクスチャを再現可能な生成スクリプトと生成済みリソースを実装済みである。
- `./gradlew build`、全JSONの構文解析、item textureの16x16 RGBA検証、ドラゴン防具entity textureの512x256 RGBA検証は成功している。
- TFC 4.2.5 と IaF CE 2.0 を導入した環境でドラゴン構造物の生成は確認済みである。実気候による属性分離は未確認である。
