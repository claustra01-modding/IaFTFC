# IaFTFC 開発ガイド

## 共通開発ルール

- 本書は作業規約と実装仕様を兼ねる。意図を決める数値、ID、条件、例外、優先順位は残し、作業履歴とコードから機械的に得られる全件一覧は載せない。
- READMEは利用者向けの短い概要とbuild入口に絞り、詳細仕様や作業履歴を重複掲載しない。
- ライセンスと第三者表示はrootの `LICENCE` 一つへ統合し、別のlicense/noticeファイルを作らない。
- 挙動、対応版、依存、ID、有効化条件、生成規則、検証手順を変えた場合は同じ変更で本書も更新する。
- 現在値は `gradle.properties`、Mod metadata、コード、同梱data、本書の生成仕様を正本とし、対象版の実JAR・公式ソースで確認する。
- 公開API、registry、tag、dataを優先し、Mixinは必要な対象へ限定する。client専用classをcommon/server側から参照しない。
- 依存JAR、展開物、解析・生成scriptは `.tmp/` に置いてGit管理外にする。仕様と生成済みresourceを正本とし、ローカルscriptだけへ仕様を閉じ込めない。
- JSONはBOMなしUTF-8。公開済みIDとworld互換性を守り、無関係な差分、依存・version更新、format変更を混ぜない。

## プロジェクトの目的

- Modのdisplay nameは`Ice and Fire and TerraFirma`とする。内部名は`IaFTFC`、Mod IDは`iaftfc`、Javaパッケージは`net.claustra01.iaftfc`のまま維持する。
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
- レシピを無効化したIaF CEのsilver／sapphire素材、鉱石、加工品、metal tool／armor、非Iron・非Dragonsteelの既存ドラゴン防具、およびIaF CE既存Dragonsteel Ingot各3種には、クライアントtooltip末尾へ赤色の`[DISABLED]`を表示する。IaF CE既存Dragonsteel Block、`silver_pile`、色名としてのdragon scale系、TFC式レシピへ移行したDragonsteel toolには表示しない。
- IaF CEのブレス地形変換へ、TFCのgrass、dirt、coarse dirt、rooted dirt、mud、farmland、grass path、raw／hardened rock、cobble／mossy cobble、rock gravelを追加する。TFC由来の変換結果は`revert=false`として岩石種・土壌種をVanillaブロックへ失わないようにする。階段、slab、wall、装置、金属は一律変換しない。TFCのlogs、planks、leaves、cropsは標準ブロックタグ経由でIaF CE本来の処理を使う。
- IaF CE本体でプレイヤーが摂取可能なドラゴン肉3種、Pixie Dust、Ambrosia、Cannoli、ドラゴン肉入り炒飯3種、Ghost Cream、Pixie Dust Milky Teaの11品へ、TFC食料定義と`#c:foods`分類を追加する。栄養カテゴリと腐敗速度はTFC 4.2.5の実データを基準にし、満腹度と特殊食品としての強さはVanilla／IaF CE本来の値を維持する。ドラゴン肉とドラゴン肉料理は通常のTFC食料より高栄養でよく、CannoliなどIaF CE側で意図的に強力な食品も一律に弱体化しない。
- Fire／Frost／Lightning StewはIaF CE本体ではfood componentを持たないドラゴン繁殖専用アイテムであるため、TFC食料化せず、プレイヤーが摂取可能になるJava変更も加えない。
- TFCの`#c:foods/meat`を`#minecraft:meat`およびIaF CEの`dragon_food_meat`へ追加し、TFCの生肉と加熱肉をドラゴンの手渡し・落下アイテムによる給餌へ対応させる。ドラゴン繁殖はIaF CE本来の属性シチュー専用条件を維持し、通常の肉では繁殖させない。
- IaF CEドラゴンの手渡し給餌と落下食材を探すAIの両方で、TFCの`FoodCapability.isRotten`が真の食材を拒否する。落下食材は探索開始後に腐敗した場合も接触時に消費せず、IaF CE本来の非腐敗食材と繁殖専用シチューの挙動は変更しない。
- Dragon Eggの属性別孵化条件はIaF CE本来の判定を維持し、Fireは点火中のTFC Firepitまたは稼働中のCharcoal Forge上でも進行し、Iceは`#tfc:any_fresh_water`でも凍結処理へ進む。停止中の設備とSalt Waterは孵化条件に含めない。LightningはIaF CEの降雨地点・天空判定を維持する。TFC気候モデルはVanillaの降雨状態と`Level.isRainingAt`へ反映されるため、IaFTFC独自の天候判定を重ねない。
- IaF CEのItem Size／Weightは、TFC 4.2.5の`item_size`実データと`ItemSizeManager`のfallback値を基準に、IaF CE 2.0 JAR内の全item modelを重複なくカテゴリ分類して定義する。標準的なblock、food、plant、stair、slab、log、chest、ingot、ore、bottle、tool、armor等は対応するTFCカテゴリと同値にし、用途や形状が異なるアイテムを名前だけで一括推測しない。
- Item Size／Weightの確定済み例外はDragon Egg=`very_large`／`very_heavy`、Dragon Skull=`huge`／`very_heavy`とする。プレイヤー装備のDragonsteel ArmorはTFCのarmor既定値に合わせて`large`／`very_heavy`、IaF CE既存品とIaFTFC独自品のドラゴン用Dragon Armorは`very_large`／`very_heavy`とする。Dragon Forgeのbrick／core／inputは特殊設備扱いせず、すべて一般BlockItemと同じ`small`／`light`とする。
- ブレス変換先のIaF CEブロックはTFCの同系統地形挙動へ合わせる。3属性のstoneはcollapse／start collapse／trigger collapse、cobblestoneとgravelはlandslide、dirt pathはlandslide支持ブロックへ追加する。IaF CEのgravel変換先は本体の`FallingReturningStateBlock`による重力落下も維持する。通常dirt／grassはTFCの同名系統と同様にこれらのタグへ追加しない。
- IaF CEの物理武器にはTFCの斬撃／刺突／打撃item tagを形状に応じて付与する。sword／axe／hoe／macuahuitlは斬撃、bow／dagger／pickaxe／spear／tridentは刺突、shovel／gauntlet／slapper／troll weaponは打撃とする。IaF CE本体の攻撃力や特殊効果は上書きしない。
- Dragon Scale Armor全12色はTFC Leather Armorと同じ部位別knapping patternで製作する。全色共通のknapping typeと色別recipe ingredientを使用し、対応色以外のScaleでは完成しないままJEIでは1つのDragon Scale knappingタブへ統合する。Helmet／Chestplate／Leggings／Bootsのどの部位でも完成時にScale 5枚を消費し、IaF CE既存の作業台レシピは同一recipe IDのknappingレシピで置換する。
- Dragon BoneはTFC Rock Knappingと同様に2本所持時に加工を開始し、最初の加工操作で1本を消費する。Axe／Hoe／Pickaxe／Shovel HeadとSword Bladeをknappingし、全toolを対応partと`#c:bones/wither`1本の縦配置で組み立てる。Dragon Fluteは専用の5×5 patternでheadを追加せずknappingから直接完成させる。Dragonbone Arrow／BowとFire／Ice／Lightning属性Swordのレシピは変更しない。
- IaF CE防具のTFC物理耐性は本体の防御段階に対応するTFC 4.2.5実値を使用する。Copper MetalはCopper、Silver MetalはBronze、Death Worm／TrollはWrought Iron、Dragon Scale／Sea SerpentはBlack Steelとする。プレイヤー用Dragonsteel Armorとドラゴン用Dragonsteel Dragon Armorは、Red／Blue Steelを各物理属性で上回る刺突70／斬撃60／打撃70とする。Sheep／Blindfold／EarplugsはLeather、Hippogryph ArmorとDragon Armorは素材に対応するTFC金属値を使用する。IaFTFC独自Dragon Armor 4系統にも対応するSteel／Black Steel／Red Steel／Blue Steel値を付与する。
- Fire／Ice／Lightning DragonはIaF CE本体の高い体力・Armor・成長補正を尊重し、追加するTFC物理耐性は刺突／斬撃／打撃各30（各約25.9%軽減）に留める。TFC 4.2.5の動物には追加entity damage resistanceがないため、それらよりやや硬い程度の補正とする。近接攻撃の物理種別は斬撃とし、ブレスや属性攻撃についてDamage Type側で物理種別が確定している場合はその種別を優先する。
- スポーン地点周辺の生成禁止距離は IaF CE の `dangerousDistanceLimit`（既定値 1000 ブロック）をそのまま使用し、IaFTFC 側では上書きしない。
- ワールド生成は、新規チャンクで決定的に動作し、既存チャンクを暗黙に変更しない設計にする。
- IaF CE の構造物 ID や TFC のバイオームタグは、対象バージョンの実物または公式ソースで確認してから固定する。
- クライアント専用クラスを共通／サーバー側から参照しない。専用サーバーでのロードを必ず考慮する。

## ドラゴンスチール統合

- `dragonsteel_fire`、`dragonsteel_ice`、`dragonsteel_lightning`をTFCの`RegistryMetal`として登録する。基準素材は順にRed Steel、Blue Steel、Black Steelとする。
- IaFTFC側のインゴットを正規の加工素材とし、IaF CE既存Dragonsteel Ingot各3種は無効化する。IaF CE既存Dragonsteel Block各3種は有効とし、Block本体と圧縮・分解レシピをIaFTFCのdatapackで上書きしない。完成品のtool／armorはIaF CE既存アイテムを維持する。
- 各金属にingot、double ingot、sheet、double sheet、rod、axe／hoe／pickaxe／shovel head、sword blade、4種のunfinished armor、block、slab、stairs、anvil、molten fluidを実装する。
- Dragon Forgeの入力はFire=`#c:ingots/red_steel`、Ice=`#c:ingots/blue_steel`、Lightning=`#c:ingots/black_steel`とし、特定のTFCアイテムIDへ固定しない。出力はIaFTFCの対応インゴットとする。
- Fire／Ice／Lightning Dragon Forge Brickの元レシピ形状、属性別Dragon Scale Block、出力数を維持し、Vanilla Stone Bricks枠だけを`tfc:fire_bricks`へ置換する。
- Dragon Forgeで完成したIaFTFCドラゴンスチールインゴットには、完成時点でTFCの温度1750℃を付与する。レシピ読込時ではなく出力スロットへ配置された直後に温度を設定する。
- IaF CE既存Dragonsteel toolレシピは、TFC式の対応tool headまたはsword bladeと木のrodの組み立てへ置換し、鍛造ボーナスを引き継ぐ。Axe／Hoe／Pickaxe／Shovel HeadはIngot 1個、Sword BladeはDouble Ingot 1個からtier 7金床で鍛造する。armorレシピはunfinished armorとsheet類の溶接へ置換する。
- ドラゴン防具はSteel、Black Steel、Red Steel、Blue Steelの4系統を追加し、各系統にhead、neck、body、tailを登録する。防御値は順に3.5、5.5、7.5、7.5とし、IaF CE既存値を含めてIron < Steel < Black Steel < Red／Blue Steel < Dragonsteelとなるよう維持する。
- Iron、3属性Dragonsteel、新規4系統のドラゴン防具は元の部位別クラフト形状を維持し、素材を対応する`#c:double_sheets/*`へ置換する。Copper、Gold、Silver、Diamond、Netheriteの既存ドラゴン防具レシピは無効化し、アイテムへ赤い`[DISABLED]`ツールチップを付与する。
- ドラゴンスチール金床はTFC Red／Blue Steelより1段階高いtier 7とする。導入経路を閉じないためdouble ingotの最初の溶接だけtier 6で行い、金床製作後のsheet、rod、全tool head／sword blade、unfinished armor、double sheet、完成armorはtier 7を要求する。
- 3属性共通で溶融温度は2000℃、鍛造可能温度は1200℃、溶接可能温度は1600℃とし、TFC最高級鋼より明確に高温を要求する。
- 表示言語は`en_us`のみを同梱し、`ja_jp`は追加しない。
- DragonsteelのテクスチャとJSON、TFC式tool head／完成toolレシピ、および3属性のDragon Forge Brickレシピは本節の仕様と生成済みresourceを正本とし、ローカル再生成には`.tmp/tools/regenerate_dragonsteel.py`を使う。TFC Metallum Overhaulの現行方式に合わせ、形状・陰影元はFire=Red Steel、Ice=Blue Steel、Lightning=Black Steelを個別に選び、色はIaF CEの対応Dragonsteel Ingotから輝度順位パレット転写する。Plated BlockとAnvil用Smooth Blockは大型面として順位幅を55%へ圧縮し、通常itemは全順位幅を使う。unfinished armorはIaF CEの対応する完成防具テクスチャを彩度55%へ落として使用する。ToolレシピはTFC Red Steelの鍛造規則・組立形式とIaF CEの出力ID、BrickレシピはIaF CE元データとTFC Fire Bricks IDをJARから検証する。再生成にはPython 3、Pillow、対象バージョンのTFC／IaF CE JARが必要である。
- 新規ドラゴン防具のレシピ、モデル、英語名、テクスチャ、Item Size／Weight定義は本節と生成済みresourceを正本とし、ローカル補助は`.tmp/tools/regenerate_dragon_armor.py`とする。テクスチャはIaF CE既存ドラゴン防具間で一致するサドル・革などの画素を維持し、地金部分だけをTFCの各double sheet配色へ変換する。エンティティ描画用テクスチャはIaF CEの描画規約に合わせて`assets/iceandfire/textures/entity/dragon_armor`へ配置する。
- ドラゴンチェストloot tableと全shared tableは生成済みdataと本節を正本とし、`.tmp/tools/regenerate_dragon_chest_loot.py`はIaF CE 2.0 JARとTFC 4.2.5 JARからのローカル再生成補助に限る。元tableとの構造・count・weight比較、profile上限、装備比率、enchantment位置、禁止金属、graphite配置、TFC item IDを検証する。
- TFC側と競合するIaF CEの銀・サファイアレシピ無効化JSONのローカル再生成補助は`.tmp/tools/regenerate_disabled_iaf_recipes.py`とする。
- IaF CE食料のTFC食料定義とドラゴン用肉タグのローカル再生成補助は`.tmp/tools/regenerate_food_compat.py`とし、TFCの基準食料、対象item、food field、栄養素、満腹度、腐敗速度を実JARから検証する。
- IaF CEアイテムのItem Size／Weight定義と分類tagのローカル再生成補助は`.tmp/tools/regenerate_iaf_item_sizes.py`とし、item modelとblockstateの全件・一意分類・TFC参照値・確定済み例外を検証する。
- 物理武器tag、防具耐性、Dragonの攻撃種別と耐性のローカル再生成補助は`.tmp/tools/regenerate_physical_damage.py`とし、対象model、entity、TFC防具耐性、全対象の一意分類を検証する。
- Dragon Scale Armor一式のローカル再生成補助は`.tmp/tools/regenerate_dragon_scale_knapping.py`とし、TFC Leather Armor pattern、IaF CEのscale/result、12色GUI textureを実物から検証する。
- Dragon Bone一式のローカル再生成補助は`.tmp/tools/regenerate_dragonbone_knapping.py`とする。Axe／Hoe／ShovelはTFC Stone Toolの実patternを中央配置の5×5へ展開する。Pickaxe／SwordはTFC Clay Moldの実patternを反転して使用し、全recipeを明示5×5として`default_on`を使わない。part textureは対応head形状へDragon Bone色を転写し、盤面はDragon Bone Block side textureを使う。
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
