#!/usr/bin/env python3
"""Prepare six no-person food-commercial reference and MiniMax H3 packages."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEQUENCES = ROOT / "sequences"


PRODUCTS = [
    {
        "slug": "hainan_coconut_coffee",
        "title": "椰奶咖啡",
        "en": "Iced Hainan Coconut Coffee",
        "asset_dir": "48_hainan_coconut_coffee",
        "source_products": ["outputs/reference_assets/48_hainan_coconut_coffee/source_products/hainan_coconut_milk_carton.png"],
        "scene": "a working Hainan coffee kitchen with sea-glass teal terrazzo prep surfaces, warm weathered teak shelves, pale sand plaster, a brushed stainless espresso machine and palm-filtered morning light; visible food-prep equipment, never café seating or a drink bar",
        "food": "a tall iced coconut coffee with clear ice cubes, dark freshly pulled coffee and smooth ivory coconut milk, finished as a natural dark-to-ivory swirl with no whipped cream, no boba and no syrupy foam cap",
        "logic": "Build the drink in a tall chilled clear glass: add clear ice cubes, pour strong cold espresso or coffee over the ice, then pour the supplied coconut milk slowly so it makes a soft ivory cloud and a gentle brown-and-cream swirl. Do not blend it into a smoothie. The finished drink must be cold, glossy and drinkable, with distinct but natural coffee and coconut layers rather than a muddy beige liquid or an artificially perfect stripe.",
        "sources": [
            ("Cuisinart: Creamy Iced Coconut Coffee", "https://www.cuisinart.com/recipes/beverages/creamy-iced-coconut-coffee-recipe.html", "椰奶可用于冰咖啡；本片采用冰块、浓咖啡和椰奶的清爽分层呈现。"),
            ("Instant Pot: Iced Coconut Coffee", "https://instantpot.com/blogs/recipes/iced-coconut-coffee", "以冰咖啡为底，椰奶从上方倒入形成自然融合。"),
        ],
        "states": {
            "scene_anchor": "Vertical no-person opening in this working Hainan coffee kitchen. The exact supplied black-and-yellow 245ml coconut-milk carton is a prominent, fully visible upright product at the left foreground; preserve its exact printing, colours and geometry without redrawing, cropping, substitution or invented text. A small physical AGO tabletop tent card from Image 1 stands at rear-right. In front: one tall empty ribbed glass, clear ice cubes, a small glass beaker of dark espresso and a stainless espresso machine behind. Keep the entire carton, glass and ingredients inside the frame; no people.",
            "prep_state": "Top three-quarter no-person coffee setup on the sea-glass terrazzo kitchen prep counter: a tall clear ribbed glass holds only clear ice cubes; a small glass beaker contains dark fresh espresso, with a small jug of ivory coconut milk waiting beside it. Teak shelving, a shelf of kitchen cups and the brushed espresso machine remain visibly consistent. No café seating, carton, tabletop card, face, body, hand or reflection.",
            "cook_state": "Close no-person kitchen pour-state image: dark espresso surrounds clear ice in the tall ribbed glass while an ivory coconut-milk ribbon has just entered and blooms into natural feathery brown-and-cream swirls. A stainless espresso machine and prep shelf blur behind. The drink is not blended and has no whipped cream, boba, jelly, foam cap, fruit garnish, package, tabletop card or person.",
            "hero_state": "Final no-person drink hero in the working Hainan coffee kitchen: a tall clear ribbed glass of iced coconut coffee holds clear ice and a refined natural dark-coffee-to-ivory-coconut gradient on a sea-glass terrazzo prep counter. A brushed-stainless espresso machine and small kitchen shelves softly blur behind. One tiny espresso bean saucer sits aside only as a subtle coffee cue. The drink remains glossy, cold and believable; no café seating, outdoor view, carton, tabletop card, people, hands, straws, boba or whipped cream.",
        },
        "titles": ["Coconut coffee kitchen setup", "Espresso and coconut swirl", "Iced coffee kitchen hero"],
        "shots": [
            [
                "A locked 40mm high three-quarter wide kitchen-prep shot begins on the complete reference-established counter layout. Keep every object already visible in <Picture 1> inside the same frame, in the same relative position, while the central tall ribbed glass, clear ice, dark espresso beaker and ivory coconut-milk jug remain readable. The sunlit Hainan coffee kitchen is empty, with no person, hand or reflection. End before any ingredient moves.",
                "Cut to a 75mm glass-height insert. Clear ice cubes settle once into the tall ribbed glass and catch the morning light; all other opening objects remain exactly where the reference establishes them. No scoop, hand or other object enters. End with clean transparent ice in the glass.",
                "Cut to a 65mm side close shot. Dark espresso flows in one controlled narrow stream from above frame around the ice, then stops. No vessel or person is visible. End with deep coffee pooled around the ice and open space above it for the next pour.",
            ],
            [
                "A locked 55mm glass-height shot begins on dark coffee and clear ice in the same tall ribbed glass. Ivory coconut milk enters from above frame in one slow narrow ribbon with no hand or vessel visible. End at the first soft cloud where the two liquids meet.",
                "Cut to an 85mm macro insert. The ivory coconut milk moves through dark coffee around clear ice in feathery, physically plausible brown-and-cream swirls. Keep the liquid cold, glossy and unblended: no foam crown, beads, jelly, fruit or opaque muddy colour. End with a natural partial gradient.",
                "Cut to a calm 65mm three-quarter glass shot. The pour has stopped and the drink settles, leaving a deep coffee base and soft ivory upper swirl with a few clear ice facets visible. The kitchen light and terrazzo remain unchanged. End ready for a clean serving hero.",
            ],
            [
                "A locked 50mm serving shot begins on the settled iced coconut coffee. The glass rotates a few degrees on the terrazzo from an unseen base movement, then becomes still; no hand or person is visible. End with the natural coffee-to-coconut gradient facing camera.",
                "Cut to an 85mm macro texture insert. Condensation beads on the ribbed glass while clear ice refracts the coffee and ivory coconut swirl. Keep all liquid layers soft and credible, never striped, muddy or smoothie-thick. End with cold glass texture sharp.",
                "Cut to a calm 60mm final kitchen hero. The tall iced coconut coffee sits centered with one tiny saucer of espresso beans set far beside it. No carton, tabletop card, straw, package, person, hand, caption or watermarked graphic is visible. End on a clean cold-coffee kitchen payoff.",
            ],
        ],
    },
    {
        "slug": "xian_beef_roujiamo",
        "title": "牛肉夹馍",
        "en": "Xi'an Beef Roujiamo",
        "asset_dir": "49_xian_beef_roujiamo",
        "source_products": ["outputs/reference_assets/49_xian_beef_roujiamo/source_products/beef_roujiamo_product_reference.png"],
        "scene": "a distinctive Xi'an street-food kitchen with pale limestone arch walls, charcoal-grey basalt worktops, a low black iron flatbread griddle, burnished brass spice tins, smoky olive linen and late-afternoon side light",
        "food": "a golden flaky layered round roujiamo flatbread, split only enough to hold moist soy-glazed chopped beef and fresh bright-green pepper pieces, with crisp toasted layers and no mayonnaise, cheese, salad leaves or pulled-pork texture",
        "logic": "Use the supplied product photo as the visual authority for the finished bread: it is a round, layered, pan-toasted flaky flatbread rather than a soft western bun. Start with already braised tender beef chopped into uneven 8–12 mm short pieces and fresh 8–10 mm green-pepper pieces. Sear the beef in a very hot black wok, add green pepper only when the beef is fragrant, then drizzle a small amount of light soy sauce around the hot wok edge and toss quickly until it reduces to a thin brown glaze. The peppers stay bright, crisp-tender and distinct; the beef stays chunky and moist, never minced, puréed or soupy. Toast the flatbread until golden, crisp and layered, split it partially, then fill it while the bread remains visibly flaky.",
        "clip1_cooks": True,
        "clip2_near_finished": True,
        "clip_states": {
            1: "chunky braised-beef pieces and bright-green pepper pieces searing and beginning to glaze with soy in a hot black wok; the round flatbread stays whole, unfilled and untoasted at the counter edge - no split bread, no filling, no assembled sandwich exists yet.",
            2: "the beef and pepper filling fully glazed in the wok, the flatbread toasted golden on the griddle, and the filling just slid into the opened bread pocket - the sandwich is freshly filled but not yet plated as the final hero shot.",
        },
        "sources": [
            ("Roujiamo recipe reference", "https://m.xiachufang.com/recipe/103436091/", "肉夹馍以炖煮入味的肉夹入圆馍；本片按牛肉、青椒和层次酥馍的指定产品视觉执行。"),
            ("Roujiamo background", "https://en.wikipedia.org/wiki/Roujiamo", "西安穆斯林地区常见孜然和胡椒调味的牛肉夹馍；仅借鉴牛肉风味逻辑。"),
            ("Soy-glazed beef and green pepper method", "https://www.baltimorechineseschool.org/activities/2021/cw/prog/recipies-cn.pdf", "牛肉先在热锅炒熟，再加入生抽快速炒至挂汁；本片将此快炒逻辑用于青椒牛肉夹馍馅。"),
        ],
        "states": {
            "scene_anchor": "Vertical no-person opening in this Xi'an street-food kitchen. Use the supplied beef roujiamo photo as the exact food-shape authority: one real finished layered golden roujiamo sits on a plain white plate at rear-left, with the same chopped beef and green-pepper filling visible but not copied as a printed image. A small physical AGO tabletop tent card from Image 1 stands at rear-right. In front: a second unfilled round layered flatbread, separate bowls of chunky braised-beef pieces and fresh green-pepper pieces, a small dish of light soy sauce, a black wok and a black iron griddle. No package, people or hands.",
            "prep_state": "Top three-quarter no-person preparation image in the Xi'an limestone-and-basalt kitchen: chunky 8–12 mm tender braised-beef pieces, fresh bright-green 8–10 mm pepper pieces and a small dark dish of light soy sauce remain clearly separate beside a smoking-hot black wok. A round layered flaky flatbread is still unfilled nearby. No tabletop card, face, body, hand, package, cheese or salad.",
            "cook_state": "Close no-person wok image in the same Xi'an kitchen: chunky braised beef and bright-green pepper pieces are actively quick-stir-fried in one black wok. A small amount of light soy sauce has reduced into a thin glistening brown coating around the distinct beef pieces; peppers are crisp-tender and remain green. The wok is hot with a controlled low steam plume, never soupy, minced, oily, raw or covered in dark sauce. The same round layered flatbread waits out of focus at the griddle edge. No card, people, hands or package.",
            "hero_state": "Final no-person street-food hero in the Xi'an kitchen: one warm golden layered roujiamo on a plain white plate is split and generously filled with moist chopped braised beef and small green-pepper cubes. The toasted layers visibly fan at the cut edge; filling stays inside and not soupy. No cheese, mayonnaise, lettuce, tomato, package, tabletop card, person, hand or utensil.",
        },
        "titles": ["Beef, green pepper and soy setup", "Quick wok filling and toast", "Layered roujiamo hero"],
        "shots": [
            [
                "A locked 45mm high three-quarter basalt-counter shot begins on the complete ingredient setup: one unfilled round layered flatbread, chunky tender braised-beef pieces, bright-green pepper pieces, a small dark dish of light soy sauce, one black wok and one black iron griddle. The Xi'an kitchen is empty with no person or hand. End with every ingredient separate and the bread's flaky circular layers readable.",
                "Cut to a 75mm overhead wok insert. The chunky cooked beef pieces settle into the hot black wok in one small release from above frame, with no bowl, utensil, hand or person visible. Keep each piece distinct and naturally irregular, never minced or wet. End as the beef begins to sizzle.",
                "Cut to a 65mm wok-level side shot. Bright-green pepper pieces enter around the beef, followed by one restrained light-soy ribbon at the far wok edge; no bottle, hand or person is visible. End as the soy begins to reduce, with peppers still clearly green.",
            ],
            [
                "A locked 55mm wok-height shot begins on beef and green pepper as the light soy reduces into a thin brown glaze. The wok gives one small unseen toss; each beef piece stays chunky and each pepper piece stays bright green and crisp-tender. No person or hand is visible. End with a contained, glistening, never soupy filling.",
                "Cut to an 80mm griddle insert. The round layered flatbread warms on the low black iron griddle and turns naturally golden at its ridged flaky surface. It remains round, layered and crisp, never a soft western bun or folded tortilla. No hand or utensil enters. End with a clean seam ready to open.",
                "Cut to a 65mm side medium close shot. The golden flatbread opens slightly at its side seam, and the completed wok filling slides once into the pocket from just above frame with no scoop, hand or person visible. Keep the filling juicy but contained: no gravy spill, cheese, mayonnaise, lettuce or tomato. End with the flaky bread freshly filled and ready for plating.",
            ],
            [
                "A locked 50mm plate-height shot begins on the finished beef roujiamo resting on a plain white plate. The plate slides a few centimetres into the center from outside frame, then stops; no hand, person or utensil appears. End on a clear cut face of beef and green pepper.",
                "Cut to an 85mm macro texture insert. Toasted flaky bread layers fan naturally around the moist chopped beef and bright green pepper cubes. Preserve crisp layers and a contained filling, avoiding soggy bread, western burger form or any extra sauce. End with appetising texture sharp.",
                "Cut to a calm 60mm final hero. The single layered beef roujiamo sits centred on the white plate against pale limestone and charcoal basalt, with no package, tabletop card, person, hand, cheese, salad or graphic text. End on a true Xi'an street-food finish.",
            ],
        ],
    },
    {
        "slug": "hong_kong_french_toast",
        "title": "港式西多士",
        "en": "Hong Kong French Toast",
        "asset_dir": "50_hong_kong_french_toast",
        "source_products": [],
        "scene": "a working Hong Kong cha chaan teng kitchen with pale mint-green wall panels, brushed chrome shelves, amber laminate prep counter, a black flat pan and warm lunchtime window light; no dining booth or seating",
        "food": "two thick crust-trimmed white-bread slices filled with a thin layer of smooth peanut butter, egg-dipped and pan-fried evenly golden, finished with one square of pale butter and a restrained glossy thread of condensed milk",
        "logic": "Spread a thin even layer of smooth peanut butter between two thick crust-trimmed white-bread slices; seal the sandwich gently, dip all sides in beaten egg, then shallow-fry until evenly deep golden and crisp without burning. Plate the toast as a tidy thick square, place one small cold butter square on top and add only a restrained condensed-milk drizzle. The centre must show peanut butter, not jam, chocolate, cheese, meat or an overflowing filling.",
        "clip2_near_finished": True,
        "clip_states": {
            1: "two crust-trimmed white-bread slices, one spread with peanut butter and closed into a sandwich, pale and untouched by egg or heat - no egg dip, no oil, no browning, no golden crust, no butter square, no condensed milk exists yet.",
            2: "the assembled sandwich now egg-dipped and pan-frying to a deep golden crust in the black flat pan - dry, unfried bread no longer exists, but it is not yet plated, buttered or drizzled with condensed milk.",
        },
        "sources": [
            ("SBS: Hong Kong-style French toast", "https://www.sbs.com.au/food/recipe/hong-kong-style-french-toast-sai-do-si/5l9pqdijr", "港式西多士以鸡蛋包裹后煎炸，并搭配黄油和炼乳；家用可用平底锅煎制。"),
            ("Hong Kong French-toast context", "https://en.wikipedia.org/wiki/French_toast", "传统港式做法常以花生酱或果酱夹两片面包后蘸蛋煎炸；本片锁定花生酱版本。"),
        ],
        "states": {
            "scene_anchor": "Vertical no-person opening in this working Hong Kong cha chaan teng back kitchen. A small physical AGO tabletop tent card from Image 1 sits far back on the amber laminate prep counter. In the foreground, show the complete recipe mise en place before any assembly: two separate thick crust-trimmed white-bread slices, a small shallow bowl of smooth peanut butter, a separate shallow bowl of beaten egg, a pale butter square, a tiny ceramic pitcher of condensed milk and one clean black flat frying pan. Pale mint panels, burner and chrome kitchen shelving are visible; no booth, table seating, people, hands, package or unrelated breakfast items.",
            "prep_state": "Top three-quarter no-person preparation image in the same cha chaan teng back kitchen: one thick, tidy peanut-butter bread sandwich has just been assembled and remains dry, square and unsoaked beside the shallow bowl of beaten egg. The same black flat pan rests on the same burner with a thin sheen of oil; pale mint panels and chrome kitchen shelves remain identical. No dining booth, tabletop card, hands, faces, package, jam, chocolate, cheese, meat or fruit.",
            "cook_state": "Close no-person pan image in the same kitchen: the one thick egg-dipped bread sandwich fries in a thin layer of oil in the same black flat pan, showing a natural deep-golden crisp surface, tiny fry bubbles and softly defined square edges. It is not burnt, soaked, breaded or covered in syrup. The butter square and condensed milk wait out of focus; no card, people, hands or package.",
            "hero_state": "Final no-person cha chaan teng kitchen hero: a thick golden square Hong Kong French toast sits on a small white oval plate at an amber laminate prep counter with a black flat pan, burner and chrome kitchen shelves softly blurred behind. One small pale butter square gently softens at centre with a restrained condensed-milk thread. One clean diagonal cut exposes a thin smooth peanut-butter layer. No dining booth, fruit, whipped cream, ice cream, jam, chocolate, package, tabletop card, person or utensil.",
        },
        "titles": ["Peanut-butter toast setup", "Golden egg-dipped fry", "Butter and condensed-milk hero"],
        "shots": [
            [
                "A locked 45mm high three-quarter wide kitchen-prep shot begins on the complete unassembled ingredient layout from <Picture 1>: two separate thick white-bread slices, smooth peanut butter in its own shallow bowl, beaten egg in a second shallow bowl, one pale butter square, a tiny condensed-milk pitcher and a clean black flat pan. Keep all ingredients fully visible and separate for the full opening beat. No person, hand or reflection is visible.",
                "Cut to a 75mm overhead insert. Smooth peanut butter spreads once into a thin even layer across one bread slice from an unseen action beyond the frame; no knife, utensil, hand or person is visible. Keep the other bread slice dry and separate. End with a clean, restrained peanut-butter layer that does not spill over the crustless edges.",
                "Cut to a 65mm bowl-height side shot. The plain top bread slice settles once onto the peanut-butter slice to make one tidy thick square sandwich. The egg bowl and black pan remain in their unchanged positions. No person or hand appears. End with the filling contained precisely at the seam and the sandwich still dry, ready for the next clip.",
            ],
            [
                "A locked 55mm bowl-height shot begins on the dry assembled sandwich beside the beaten egg bowl. The sandwich lowers once into the egg from just above frame with no person, hand or utensil visible, coating every face in a thin even layer without pooling or bread crumbs. End when the egg dip is complete.",
                "Cut to an 80mm pan-height close insert. The egg-dipped sandwich settles once into a thin sheen of oil in the same black flat pan, then develops a natural deep-golden crust with tiny fry bubbles and crisp square edges. It is neither burnt nor excessively dark, with no syrup, crumbs, cheese or leaking filling. End on a fully golden first side.",
                "Cut to a 65mm side medium close shot. The golden toast rests at the pan edge for one calm beat, allowing excess oil to settle away. The amber laminate, mint walls, burner and chrome kitchen shelves remain unchanged. End ready for plating.",
            ],
            [
                "A locked 50mm plate-height shot begins on the golden square toast centred on a small white oval plate. One pale butter square settles gently at its centre from above frame; no hand or utensil is visible. End before the butter melts completely.",
                "Cut to an 85mm macro insert. A restrained narrow thread of condensed milk appears once from just above frame, crossing the golden surface beside the softening butter. It stops cleanly: no syrup lake, whipped cream, ice cream or fruit enters. End with crisp crust and creamy accents sharp.",
                "Cut to a calm 60mm final kitchen hero. One diagonal cut reveals the thin smooth peanut-butter layer inside the thick golden toast. No package, tabletop card, person, hand, utensils, extra breakfast dishes or graphic text is visible. End on a neat cha chaan teng kitchen payoff.",
            ],
        ],
    },
    {
        "slug": "japanese_ketchup_omurice",
        "title": "日本番茄酱蛋包饭",
        "en": "Japanese Ketchup Omurice",
        "asset_dir": "51_japanese_ketchup_omurice",
        "source_products": [],
        "scene": "a retro Tokyo kissaten kitchen with tobacco-brown Formica counter edges, cream porthole tiles, muted persimmon cabinet fronts, a small brushed-steel frying pan, old brass lamp glow and gentle early-evening light",
        "food": "a neat oval mound of ketchup fried rice with small cooked chicken-thigh pieces, onion and mushroom, covered in a smooth thin pale-yellow omelette and finished with one unbroken modest ketchup ribbon",
        "logic": "Cook small 5 mm chicken-thigh pieces, onion and mushroom, add cold cooked rice, then briefly fry ketchup and finish with butter so the grains become glossy orange-red but remain distinct. Shape the rice as a tidy low oval. Cook a thin smooth omelette just set at the edge and tender in the centre, wrap it around the rice, then add a single simple ketchup ribbon with no writing. Do not use an overstuffed omelette, torn egg, red sauce puddle, runny raw egg, western cheese filling or decorative ketchup lettering.",
        "sources": [
            ("Japan Rice: Omurice", "https://myjapanrice.com/en/recipe/ketchup-fried-rice-with-omelet/", "番茄酱炒饭由鸡肉、洋葱、蘑菇、米饭和番茄酱炒制，搭配薄蛋皮包裹。"),
            ("Just One Cookbook: Omurice", "https://www.justonecookbook.com/omurice-japanese-omelette-rice/", "日式蛋包饭以番茄调味鸡肉饭配柔软蛋皮为核心；本片采用经典闭合蛋包形式。"),
        ],
        "states": {
            "scene_anchor": "Vertical no-person opening in this retro Tokyo kissaten kitchen. A small physical AGO tabletop tent card from Image 1 stands far back on the brown Formica counter. In front: a bowl of cold cooked rice, tiny 5 mm chicken-thigh pieces, minced onion, sliced mushroom, a small ketchup dish, two eggs, butter and a brushed-steel frying pan. No person, hand, package or unrelated Japanese dishes.",
            "prep_state": "Top three-quarter no-person preparation image in the Tokyo kissaten: tiny cooked chicken-thigh pieces, minced onion and sliced mushroom sit with cold rice and ketchup in clearly separate small dishes; beaten eggs wait in a glass bowl. The brushed-steel pan warms at rear. No tabletop card, hands, face, body, package, cheese or raw chicken.",
            "cook_state": "Close no-person pan image: individual rice grains are glossy orange-red from ketchup and butter with tiny fully cooked chicken, onion and mushroom. A thin pale-yellow omelette disk is just set in a second small brushed-steel pan, smooth and flexible without brown spots or raw liquid. No card, people, hands, package or sauce puddle.",
            "hero_state": "Final no-person Tokyo kissaten kitchen hero: a thin handmade pale-yellow omelette with subtle fold creases and naturally uneven egg edges wraps a low oval of ketchup fried rice. The egg has a gentle buttery satin sheen and must not be an inflated pillow; use only one narrow irregular ketchup line, with no writing. Brown Formica counter edges, a small pan burner and cream porthole tiles softly blur behind. No dining booth, cheese, side salad, package, tabletop card, person, hand or utensil.",
        },
        "titles": ["Ketchup rice mise en place", "Glossy rice and thin omelette", "Classic omurice hero"],
        "shots": [
            [
                "A locked 45mm high three-quarter Formica-counter shot begins on cold cooked rice, tiny cooked chicken-thigh pieces, minced onion, sliced mushroom, a small ketchup dish, two eggs, butter and a brushed-steel pan. No person, hand or reflection appears. End with each ingredient distinct and accurately small.",
                "Cut to a 75mm pan-height insert. Tiny chicken, onion and mushroom pieces warm together in the pan until they look fully cooked and lightly glossy. No raw meat remains and no utensil or hand enters. End ready for rice.",
                "Cut to a 65mm close shot. Cold rice settles in the pan and ketchup coats the grains into a glossy orange-red rice, with butter giving only a soft sheen. Keep grains separate, not wet or mushy. End with an even ketchup-rice state.",
            ],
            [
                "A locked 55mm pan shot begins on the completed glossy ketchup fried rice. The rice gathers into a tidy low oval in the pan through a subtle unseen pan movement, without a hand visible. End with a clean oval mound ready for its egg cover.",
                "Cut to an 80mm close insert. In the same kitchen, a thin pale-yellow omelette disk sets in a second small brushed-steel pan: edge just firm, centre tender, surface smooth and unbroken. No raw liquid, brown spots, cheese or person appears. End while it remains flexible.",
                "Cut to a 65mm side medium close shot. The thin omelette settles over the low rice oval and folds around it cleanly, forming a smooth closed packet. The camera stays stable; end with no rice spilling out and no tear in the egg.",
            ],
            [
                "A locked 50mm plate-height shot begins on the smooth closed omurice centred on a plain cream plate. A modest ketchup ribbon descends once from above frame across the top, with no bottle, hand or writing. End as the single ribbon stops cleanly.",
                "Cut to an 85mm macro insert. Warm light catches the tender smooth egg surface, the small glossy ketchup ribbon and a barely visible low oval silhouette of rice beneath. Keep the egg pale yellow and intact: no raw runny crack, red sauce pool or lettering. End sharp and appetising.",
                "Cut to a calm 60mm final kissaten kitchen hero. The wrapped omurice sits alone on the cream plate against the same brown Formica, pan burner and porthole-tile kitchen setting. No tabletop card, package, person, hand, utensil, cheese or side salad is visible. End on a classic Japanese comfort-food kitchen finish.",
            ],
        ],
    },
    {
        "slug": "indonesian_grilled_chicken_leg",
        "title": "印尼风味烤鸡腿",
        "en": "Indonesian Grilled Chicken Leg",
        "asset_dir": "52_indonesian_grilled_chicken_leg",
        "source_products": [],
        "scene": "an open-air Javanese home grill kitchen with terracotta brick counter, cobalt batik-pattern tile splashback, a low charcoal grill, a banana-leaf-lined tray and golden tropical dusk light; no wok, braising pot, saucepan or oven",
        "food": "one fully cooked bone-in chicken leg with natural deep-mahogany kecap-manis glaze, controlled caramelised char at the edges, bright lime, a small sambal dish and a few cucumber slices, never breaded, saucy or pink inside",
        "logic": "Make ayam bakar directly on the charcoal grill, never in a wok or pot: marinate one bone-in chicken leg in a fragrant paste of shallot, garlic, ginger, turmeric, coriander, bruised lemongrass and sweet soy sauce. Put it directly over calm medium charcoal, turn it through the grill cycle until fully cooked, then brush only thin coats of sweet-soy glaze until the skin turns deep mahogany with controlled dark char at a few edges. The chicken must be fully cooked, never pink, raw, breaded, blackened all over or drowned in sauce.",
        "sources": [
            ("Spice Island Indonesia: Ayam Bakar", "https://www.spiceislandindonesia.com/recipes/ayam-bakar", "本片仅借鉴印尼香料和甜酱油风味；依用户指定改为腌制后直接炭烤，不呈现锅炖步骤。"),
            ("GlobeNosh: Javanese Ayam Bakar", "https://globenosh.com/recipes/ayam-bakar-indonesian-grilled-chicken/r1652", "本片锁定中火炭烤、分次薄刷甜酱油和局部焦糖化的视觉结果，不使用锅或汤汁。"),
        ],
        "states": {
            "scene_anchor": "Vertical no-person opening in this open-air Javanese grill kitchen. A small physical AGO tabletop tent card from Image 1 rests far back on the terracotta counter. In front: one raw bone-in chicken leg, shallot, garlic, ginger, turmeric, coriander, bruised lemongrass, a small bowl of dark sweet soy sauce, a shallow banana-leaf-lined marinating tray and the low charcoal grill. No wok, pot, saucepan, oven, people, hands, package, rice or other meats.",
            "prep_state": "Top three-quarter no-person preparation image in the Javanese grill kitchen: one bone-in chicken leg is coated in a warm yellow-brown aromatic spice paste on the same shallow banana-leaf-lined marinating tray beside sliced shallot, garlic, ginger, turmeric, coriander, bruised lemongrass and sweet soy sauce. The same low charcoal grill is ready at rear; no wok, pot, saucepan, tabletop card, face, body, hand, breading, rice or package.",
            "cook_state": "Close no-person direct-charcoal-grill image: the same chicken leg rests directly over calm medium charcoal and receives a thin glossy deep-mahogany sweet-soy glaze from above frame, with no brush, hand or person visible. The skin has a few controlled caramelised dark edges while most surface stays burnished and appetising. No pink meat, no blackened coating, no wok, no pot, no card, package or sauce flood.",
            "hero_state": "Final no-person Indonesian dinner hero in the Javanese kitchen: one fully cooked lacquered deep-mahogany grilled chicken leg rests on a banana-leaf-lined tray with a small lime wedge, a tiny sambal dish and a few cucumber slices. Skin is glossy with sparse controlled char; no rice mound, breading, raw centre, package, tabletop card, person, hand or utensil.",
        },
        "titles": ["Aromatic ayam bakar setup", "Braise, glaze and charcoal finish", "Lacquered chicken-leg hero"],
        "shots": [
            [
                "A locked 45mm high three-quarter terracotta-counter shot begins on one bone-in chicken leg, shallot, garlic, ginger, turmeric, coriander, bruised lemongrass, dark sweet soy sauce, one shallow banana-leaf-lined marinating tray and the low charcoal grill. The tropical dusk grill kitchen is empty; no person, hand or reflection appears. End with every aromatic distinct and the chicken leg whole; no wok, pot, saucepan or oven exists anywhere in the set.",
                "Cut to a 75mm overhead insert. A warm yellow-brown aromatic paste coats the chicken leg in a natural thin layer, with no visible hand or brush. The leg stays whole and unbreaded. End with the seasoning clinging to the skin.",
                "Cut to a 65mm grill-height side shot. The seasoned leg settles directly onto the calm medium charcoal grate from above frame with no person or utensil visible. Keep it whole, unbreaded and free of liquid; no pot, wok, saucepan or oven enters. End at the first quiet grill sizzle.",
            ],
            [
                "A locked 55mm charcoal-grill shot begins on the seasoned chicken leg directly over calm medium charcoal. It cooks through gradually as the skin turns from spice-coated yellow-brown to opaque deep brown; no hand, person, pot, wok, saucepan or oven appears. End with fully cooked opaque meat and a modest dry sheen.",
                "Cut to an 80mm charcoal-grill insert. The fully cooked leg rests directly over the same calm medium charcoal and deepens from brown to burnished mahogany. A few edges pick up controlled dark char, never a blackened crust. End with realistic grill heat and no excessive smoke.",
                "Cut to a 65mm grill-side medium close shot. A final thin sheen of sweet-soy glaze appears across the leg from just above frame, without brush or hand visible, then settles into a sticky glaze. End with the leg fully cooked, lacquered and ready to rest.",
            ],
            [
                "A locked 50mm tray-height shot begins on the lacquered fully cooked chicken leg as it settles onto a banana-leaf-lined tray. The leg is placed without any visible hand or utensil. End with the deep-mahogany glaze and bone-in form centered.",
                "Cut to an 85mm macro texture insert. Golden dusk light catches the glossy caramelised skin, sparse dark grill edges and the fully cooked opaque meat at one small natural cut. Keep no pink centre, breading, sauce puddle or blackened sugar coating. End with convincing sticky char texture.",
                "Cut to a calm 60mm final hero. The single grilled chicken leg rests with a lime wedge, tiny sambal dish and a few cucumber slices on its banana-leaf tray. No rice mound, package, tabletop card, person, hand, utensil or graphic text is visible. End on a real Indonesian grilled-chicken payoff.",
            ],
        ],
    },
    {
        "slug": "homestyle_double_skin_milk",
        "title": "家常双皮奶",
        "en": "Homestyle Double Skin Milk",
        "asset_dir": "53_homestyle_double_skin_milk",
        "source_products": [],
        "scene": "a quiet Shunde home dessert kitchen with milk-white enamel wall panels, warm honey-oak cabinetry, brushed brass shelf rails, a small stainless steaming pot, pale celadon porcelain bowls and soft rain-lit afternoon window light",
        "food": "a warm ivory double-skin milk custard made only from full-fat milk, egg white and sugar, with a visibly delicate intact top milk skin and a glossy tender set beneath, served plain without fruit, beans, boba, cream or heavy garnish",
        "logic": "Heat full-fat milk until steaming but not hard boiling, pour it into one pale celadon bowl and let it cool undisturbed to form the first delicate milk skin. Gently pour the milk out from one side while keeping that skin in the bowl. Add separated clear egg white and sugar to the drained warm milk, gently beat only until fully homogeneous and never foamy, then pass it through a fine sieve. Slowly return the strained mixture along the inner bowl wall under the first skin so the skin floats back to the surface. Tightly cover the bowl with clear cling film, prick only two or three tiny steam holes, then steam it in the same compact stainless pot until softly set. The final dessert has a delicate intact second skin, an ivory silky surface and no bubbles, cracks, scrambled egg, fruit, red bean, boba, jelly or artificial gloss.",
        # clip2_near_finished intentionally left unset: clip 2 ends on a
        # wrapped, steaming bowl, not the unwrapped finished custard, so
        # hero_state must not be attached to clip 2 here.
        "clip1_exclude": ["prep_state"],
        "clip_states": {
            1: "warm full-fat milk in one pale celadon bowl, its first delicate milk skin, and the same milk drained off to one side - no custard exists yet, no set texture, no second skin, no steaming, no cling film, no finished bowl.",
            2: "the strained milk-and-egg-white mixture returned beneath the first skin, then tightly wrapped in cling film and steaming inside the stainless pot - the custard is not yet set, unwrapped, or plated as the finished dessert.",
        },
        "sources": [
            ("Huang Kitchen: Double Skin Milk Pudding", "https://huangkitchen.com/double-skin-milk-pudding/", "全脂奶、蛋白和糖为核心；回倒时需让奶皮浮起，并覆膜蒸制以防蒸汽水滴。"),
            ("Buydeem: Homemade Double Skin Milk", "https://m.buydeem.cn/life-home/recipes-1037.html", "牛奶蛋清糖液过筛后回倒入留有奶皮的碗，覆保鲜膜扎孔再蒸，和本片过程一致。"),
            ("Blender & Basil: Shuang Pi Nai", "https://blenderandbasil.com/2017/06/15/double-layer-milk-shuang-pi-nai-a-simple-chinese-dessert-recipe/", "牛奶冷却形成奶皮后，与蛋白糖液混合回倒，覆膜蒸熟并静置。"),
        ],
        "states": {
            "scene_anchor": "Vertical no-person opening in this Shunde dessert kitchen. A small physical AGO tabletop tent card from Image 1 stands far back on the honey-oak counter. In front: one small stainless saucepan of steaming full-fat milk, two identical pale celadon porcelain bowls, a glass bowl of separated clear egg whites, white sugar, fine sieve, a small wire whisk, clear cling film and the same compact stainless steaming pot. No people, hands, package, fruit, beans, boba or other dessert toppings.",
            "prep_state": "Close no-person egg-separation image in the same Shunde dessert kitchen: at left, the original pale celadon bowl holds only one delicate intact first milk skin after its milk was gently drained; at centre, a clear glass bowl rests on the counter with separated raw egg white that is translucent and slightly warm pale-yellow, while the removed orange-yellow yolks rest in a separate small white bowl. Drained warm milk and white sugar wait beside the egg white. Nothing floats in the air. The same saucepan and same compact stainless steaming pot remain visible and unchanged. No tabletop card, face, body, hand, package, fruit, beans, boba or foam.",
            "cook_state": "Close no-person steam-ready image in the same Shunde kitchen: the strained milk-and-egg-white mixture has been returned under the intact first skin in the original pale celadon bowl. A clear sheet of cling film is tightly sealed across that bowl's rim with only three tiny pinholes. The bowl sits inside the exact same compact stainless steaming pot, with its matching lid resting beside it; no water droplets touch the custard. No card, people, hands, package, fruit, beans, boba or foam.",
            "hero_state": "Final no-person Shunde dessert hero in the same kitchen: the original pale celadon bowl of warm ivory double-skin milk sits on the same honey-oak counter with its intact delicate second milk skin and silky set custard beneath. The top is dry, fine and naturally satin, with no bubble, crack or water drop; one small white porcelain spoon rests beside the bowl. Keep it plain and restrained: no fruit, red bean, boba, jelly, cream, package, tabletop card, person or hand.",
        },
        "titles": ["Milk skin and egg-white setup", "Strain, return, wrap and steam", "Silky double-skin milk hero"],
        "shots": [
            [
                "A locked 45mm high three-quarter honey-oak counter shot begins on one small stainless saucepan of steaming full-fat milk, two matching pale celadon bowls, separated clear egg whites, white sugar, fine sieve, a small wire whisk, clear cling film and the same compact stainless steaming pot. The Shunde dessert kitchen is empty with no person, hand or reflection. End with every simple dairy ingredient and the one shared pot readable.",
                "Cut to a 75mm bowl-height insert. Warm ivory milk rests quietly in a pale celadon bowl and cools until one delicate translucent first milk skin forms across its surface. No spoon or hand disturbs it. End with the skin intact and visible.",
                "Cut to a 65mm side close shot. The milk pours slowly out from one side of the bowl just beneath the intact skin into a clear mixing bowl, leaving the skin floating in place. No vessel, hand or person is visible. End with the first skin preserved for return and the drained milk ready for egg white.",
            ],
            [
                "A locked 55mm countertop close shot begins on a stable glass bowl of separated raw egg white with a slight translucent pale-yellow tint, a separate white bowl of intact yolks, drained warm milk and white sugar. The egg-white bowl tilts once from an unseen support so its contents move cleanly into the milk; no airborne shell, hand or person appears. End with yolks still separate and only egg white in the milk.",
                "Cut to an 80mm mixing-bowl insert. A small wire whisk makes exactly two slow circles in the milk, egg white and sugar; the liquid becomes evenly ivory and silky without foam, bubbles, streaks or egg strands. End with the mixture homogeneous and ready to filter.",
                "Cut to a 65mm fine-sieve side close shot. The smooth mixture passes through the fine sieve and returns slowly along the inner wall beneath the intact first milk skin in the original pale celadon bowl. The skin rises naturally back to the surface without tearing. End with one even ivory surface and one delicate skin, ready for protective film in the next clip.",
            ],
            [
                "A locked 50mm steamer shot begins as a clear sheet of cling film settles tightly across the prepared celadon bowl rim with only three tiny holes, then the wrapped bowl sits inside the same compact stainless steaming pot with soft controlled steam. The pot lid and then the clear film lift out of frame once without a visible hand, revealing an ivory custard with an unbroken delicate top skin. End with no droplets, bubbles or cracks.",
                "Cut to an 85mm macro texture insert. Soft rain-lit afternoon light moves across the delicate milk skin and tender satin ivory custard below it. Keep the dessert plain, natural and silky: no fruit, beans, boba, jelly, cream or artificial mirror shine. End with the top skin sharply visible.",
                "Cut to a calm 60mm final dessert hero. The original pale celadon bowl of warm double-skin milk sits with a small white porcelain spoon beside it on the same honey oak, with the same white enamel wall and brass rail behind. No tabletop card, package, person, hand, fruit topping or graphic text is visible. End on a quiet homestyle Cantonese dessert finish.",
            ],
        ],
    },
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def reference_prompt(p: dict, kind: str) -> str:
    source_line = ""
    if kind == "scene_anchor" and p["source_products"]:
        source_line = "Image 2 is the approved supplied product reference. Preserve it faithfully only where the scene specifies it: never redraw, relabel, translate, substitute or invent it. "
    return f"""Use case: ads-marketing
Asset type: no-person MiniMax H3 R2V reference image for a vertical food commercial
Primary request: create the {kind.replace('_', ' ')} reference for {p['en']}.
Input image: Image 1 is the approved ASIAN GROCER ONLINE / powered by UMALL tabletop sign artwork; preserve it only where the scene asks for a physical tabletop card. {source_line}
Scene/backdrop: {p['scene']}.
Subject: {p['states'][kind]}
Food authority: {p['food']}.
Style/medium: premium photorealistic grocery food-commercial still, genuine cookware, credible food texture, physically plausible heat, steam or liquid behaviour.
Composition/framing: vertical 9:16, one clear food state, no face, body, portrait, person, hand, shadow or reflection.
Lighting/mood: precise directional food light, coherent shadows and clean high-end highlights.
Constraints: {p['logic']} No fake labels, captions, price graphics, watermarks, invented products or unrelated dishes.
Avoid: warped tools, melted food, excessive steam, clutter, fake app interface and any human visibility.
"""


REF_KIND_LABELS = {
    "scene_anchor": "the no-person scene and dish-identity anchor",
    "prep_state": "the preparation state",
    "cook_state": "the cooking or assembly state",
    "hero_state": "the finished serving-state target",
}


def ref_kinds_for(p: dict, clip_no: int) -> list[str]:
    """Which reference-asset kinds this clip's ref_images should contain.

    2026-08-31: clip 1 used to get all four assets unconditionally, including
    `cook_state` and `hero_state` - pictures of stages that clip has not
    reached yet. An attached picture with no demotion is not neutral (see
    CURRENT_WORKFLOW.md section 4b): `hong_kong_french_toast` clip 1 landed on
    the fully fried, plated hero shot instead of the dry unfried sandwich its
    own shots describe, and clip 2 then inherited that wrong last frame and
    regressed to an earlier action instead of continuing. Section 4c has the
    full write-up.

    Default is conservative: clip 1 only gets `scene_anchor` + `prep_state`,
    clip 2 adds `cook_state` but not `hero_state`, clip 3 gets the full arc
    including `hero_state` since it is the one clip meant to land on it. Set
    `clip1_cooks: True` on a dish whose clip 1 shots genuinely begin cooking
    (`xian_beef_roujiamo` sears beef in clip 1) to add `cook_state` there too.
    Set `clip2_near_finished: True` when clip 2's own shots end at essentially
    the finished dish (a fried, plated result) to add `hero_state` back in;
    leave it unset when clip 2 ends on an intermediate state that is not the
    finished dish (`homestyle_double_skin_milk` clip 2 ends on a wrapped,
    steaming bowl, not the unwrapped custard).
    """
    if clip_no == 1:
        kinds = ["scene_anchor", "prep_state"]
        if p.get("clip1_cooks"):
            kinds.append("cook_state")
        for excluded in p.get("clip1_exclude", ()):
            # Escape hatch for a dish-specific bad asset, not a structural
            # rule - e.g. homestyle_double_skin_milk's own `prep_state` image
            # shows already-separated egg (yolks in a bowl) because that same
            # asset is reused as clip 2's food-state reference; correct for
            # clip 2, wrong for clip 1, which should stay egg-free. Dropping
            # it here means clip 1 relies on `scene_anchor` alone, which
            # already carries the full pre-cook ingredient layout.
            if excluded in kinds:
                kinds.remove(excluded)
        return kinds
    if clip_no == 2:
        kinds = ["scene_anchor", "prep_state", "cook_state"]
        if p.get("clip2_near_finished"):
            kinds.append("hero_state")
        return kinds
    return ["scene_anchor", "cook_state", "hero_state"]


def food_line_for(p: dict, clip_no: int) -> str:
    """The closing 'Across all shots retain...' sentence, scoped to what this
    clip has actually reached. `p['food']` is the *finished* dish - correct
    verbatim only for clip 3. Reusing it verbatim on clip 1 and clip 2 was the
    other half of the 2026-08-31 bug: the text asserted the fried/set/finished
    dish in clips that had not cooked it yet. Define `clip_states: {1: "...",
    2: "..."}` on a dish with a positive description of what that clip's own
    shots actually show (see the three dishes fixed 2026-08-31 for the
    pattern) for a precise fix; otherwise a generic guard is used, which is
    safer than the old bug but weaker than a hand-written positive state.
    """
    if clip_no == 3:
        return f"Across all shots retain {p['food']}."
    interim = p.get("clip_states", {}).get(clip_no)
    if interim:
        return (f"Across all shots this clip stays at: {interim} Do not let this "
                f"clip land on, cut to, or preview the finished {p['en']}; that "
                f"state belongs only to the later clip(s).")
    return (f"This clip has not yet reached the finished {p['en']}. Show only the "
            f"ingredient and cooking state described in the shots above for this "
            f"clip; do not let this clip's final frame resemble, cut to, or "
            f"preview the completed, plated dish.")


def h3_prompt(p: dict, clip_no: int) -> str:
    kinds = ref_kinds_for(p, clip_no)
    prior = [f"the exact final frame of clip {clip_no - 1:02d}"] if clip_no > 1 else []
    refs = prior + [REF_KIND_LABELS[k] for k in kinds]
    definitions = "\n".join(f"<Picture {i}> is {value}." for i, value in enumerate(refs, 1))
    cut_times = {1: "", 2: " At 00:01.600,", 3: " At 00:03.400,"}
    shot_lines = [f"[Shot {i}]{cut_times[i]} {text}" for i, text in enumerate(p["shots"][clip_no - 1], 1)]
    spatial_ref = 1 if clip_no == 1 else 2
    # Normally the picture right after the spatial anchor is the food-state
    # authority. When `clip1_exclude` leaves only one own-picture (e.g.
    # homestyle_double_skin_milk clip 1), there is no second picture to point
    # at - fall back to the same one, since with only one image it already
    # has to carry both jobs. Referencing a <Picture N> that subject_definitions
    # never declares is a dangling reference, not just an imprecise one.
    food_ref = spatial_ref + 1 if spatial_ref + 1 <= len(refs) else spatial_ref
    retention_lines = [f"<Picture {spatial_ref}>: fully_preserved. It anchors the unique kitchen, counter, vessel, camera height, light direction and empty-set treatment."]
    if food_ref != spatial_ref:
        retention_lines.append(f"<Picture {food_ref}>: fully_preserved. It preserves the exact ingredients, cut size, colour, sheen and stage of preparation.")
    else:
        retention_lines[-1] += " It is also the food-state authority for this clip: preserve ingredients, cut size, colour, sheen and stage of preparation exactly."
    retention_block = "\n".join(retention_lines)
    if food_ref == spatial_ref:
        continuity_lead = f"Treat <Picture {spatial_ref}> as the only spatial, lighting and food-state authority."
        continuity_food = "Preserve ingredients, cut size, colour, sheen and cooking stage exactly."
    else:
        continuity_lead = f"Treat <Picture {spatial_ref}> as the only spatial and lighting bible."
        continuity_food = f"Treat <Picture {food_ref}> as the food-state authority: preserve ingredients, cut size, colour, sheen and cooking stage exactly."
    return f"""subject_definitions:
<Subject 1> is the dish and essential cookware only. No human person is a subject, visible actor, reflection or shadow.
{definitions}

summary:
reference generation. A five-second vertical no-person food commercial, clip {clip_no} of three, for {p['en']}. It advances exactly one true preparation state while retaining the same kitchen materials, light direction, cookware and food identity from the local reference stack.

retention_analysis:
<Subject 1>: fully_preserved. Food, ingredient sizes, cookware, liquid behaviour and all no-person restrictions remain physically coherent.
{retention_block}
Food sequence: fully_preserved. {p['logic']}
Human visibility: fully_preserved. Never reveal a face, head, torso, arm, hand, reflection, shadow or portrait.

detailed_description:
{chr(10).join(chr(10) + line for line in shot_lines)}

[Continuity guard] {continuity_lead} Keep counter material, wall treatment, pan, pot, glass, grill, steamer or bowl identical throughout the clip. {continuity_food} No food may appear, disappear, melt, float or transform without the named motion. Keep every human entirely out of frame, including reflections in metal, glass, windows and polished surfaces. Hold each endpoint cleanly for the next clip to inherit.

[Frame discipline] Keep food central in every frame, with one vessel and one action clearly readable. Do not introduce decorative props that obscure the ingredient state. Maintain believable gravity, liquid level, heat, steam and condensation. Preserve clean negative space and avoid sudden changes in time of day, colour temperature or table layout. The camera is rigid within each shot and every movement is small, deliberate and physically motivated.

{food_line_for(p, clip_no)} Use cuts only at 00:01.600 and 00:03.400, with one physical action per shot and stable camera. Keep cookware rigid, steam controlled and food texture coherent at every moment. Do not add people, faces, bodies, hands, shadows, reflections, captions, subtitles, title cards, price graphics, watermarks, fake labels, shopping UI, camera shake, scene jumps, warped tools, extra fingers, a different cuisine or a different dish identity. Avoid blank endings and excessive close-ups of non-food objects.

overall_soundscape:
Natural food-preparation ambience only: gentle simmer, pan sizzle, grill crackle, espresso pour, ice clink, steamer vapour and ceramic placement as physically appropriate. No dialogue.

non_diegetic_music:
Restrained premium food-commercial instrumental with a clean three-shot cadence and no vocals.
"""


def sequence(p: dict) -> dict:
    base = f"../sequence_outputs/{p['slug']}/preproduction"
    assets = f"../outputs/reference_assets/{p['asset_dir']}/generated"

    def refs_for(clip_no: int) -> list[str]:
        return [f"{assets}/{p['slug']}_{kind}-1.png" for kind in ref_kinds_for(p, clip_no)]

    return {
        "sequence_id": f"{p['slug']}_3x5_native1080",
        "server": "http://127.0.0.1:8189",
        "defaults": {"mode": "r2v", "width": 1088, "height": 1920, "duration": 5.0, "steps": 8, "turbo": True, "turbo_low_vram": True, "no_audio": True, "ref_image_size": "match", "poll": 10, "timeout": 10800},
        "clips": [
            {"id": "clip-01-prep-hook", "prompt_file": f"{base}/h3_prompts/clip_01_ref2va.md", "ref_images": refs_for(1), "seed": 202608300101, "prefix": f"sequence/{p['slug']}_3x5_native1080/clip-01"},
            {"id": "clip-02-cook-proof", "prompt_file": f"{base}/h3_prompts/clip_02_ref2va.md", "use_previous_last_frame_as_ref": True, "ref_images": refs_for(2), "seed": 202608300102, "prefix": f"sequence/{p['slug']}_3x5_native1080/clip-02"},
            {"id": "clip-03-serving-hero", "prompt_file": f"{base}/h3_prompts/clip_03_ref2va.md", "use_previous_last_frame_as_ref": True, "ref_images": refs_for(3), "seed": 202608300103, "prefix": f"sequence/{p['slug']}_3x5_native1080/clip-03"},
        ],
        "final": {"filename": f"{p['slug']}_3x5_native_1080x1920.mp4", "concat_mode": "both", "crop": {"width": 1080, "height": 1920, "x": 4, "y": 0}, "crf": 16, "preset": "medium", "keep_audio": False},
    }


def package(p: dict) -> None:
    pre = ROOT / "sequence_outputs" / p["slug"] / "preproduction"
    write(pre / "recipe_bible.md", f"""# {p['title']} — 无真人制作圣经

## Recipe logic

{p['logic']}

## Visual rule

No visible person, hands, human reflection or human shadow. The opening reference frame uses the physical AGO tabletop card. Where a source product reference exists, the opening reference preserves that supplied product exactly. H3 video prompts deliberately contain no company name, sign instruction or product-brand wording.

## Reference states

1. Opening — {p['states']['scene_anchor']}
2. Prep — {p['states']['prep_state']}
3. Cook / assembly — {p['states']['cook_state']}
4. Hero — {p['states']['hero_state']}
""")
    write(pre / "recipe_sources.md", "# Recipe Sources\n\n" + "\n".join(f"- [{name}]({url}) — {note}" for name, url, note in p["sources"]))
    for kind in ["scene_anchor", "prep_state", "cook_state", "hero_state"]:
        write(pre / "reference_prompts" / f"{kind}.md", reference_prompt(p, kind))
    storyboard = [f"# {p['title']} — 无真人 3×5s 分镜", "", "三个独立的 5 秒 H3 R2V 片段。所有镜头无真人、无手、无倒影。", ""]
    for number, (title, shots) in enumerate(zip(p["titles"], p["shots"]), 1):
        storyboard += [f"## Clip {number}: {title}", "", *[f"- {shot}" for shot in shots], ""]
    write(pre / "storyboard.md", "\n".join(storyboard))
    # CAUTION: this clobbers clip_01/02/03_ref2va.md unconditionally. Several
    # dishes carry hand-edits on top of what this script would regenerate:
    # the 2026-08-31 clip-1 fixes (ref_kinds_for/food_line_for now reproduce
    # those), and homestyle_double_skin_milk's clip 2, which was hand-wired
    # to two extra pictures (cracked_egg_state, egg_white_mix_state) this
    # generic path has no concept of and will not restore. Re-running
    # `main()`/`package()` for a dish you have hand-tuned will silently
    # discard that tuning - diff before overwriting.
    for number in range(1, 4):
        write(pre / "h3_prompts" / f"clip_{number:02d}_ref2va.md", h3_prompt(p, number))
    assets = {kind: f"outputs/reference_assets/{p['asset_dir']}/generated/{p['slug']}_{kind}-1.png" for kind in ["scene_anchor", "prep_state", "cook_state", "hero_state"]}
    if p["slug"] == "homestyle_double_skin_milk":
        assets["cracked_egg_state"] = f"outputs/reference_assets/{p['asset_dir']}/generated/{p['slug']}_cracked_egg_state-1.png"
        assets["egg_white_mix_state"] = f"outputs/reference_assets/{p['asset_dir']}/generated/{p['slug']}_egg_white_mix_state-1.png"
    manifest = {
        "product": p["title"],
        "dish_identity": p["food"],
        "physical_sign_reference": "../../../company_logo/AGO.png",
        "source_product_images": p["source_products"],
        "assets": assets,
        "generation_order": list(assets),
    }
    write(pre / "reference_manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    write(SEQUENCES / f"{p['slug']}_3x5_1080.json", json.dumps(sequence(p), ensure_ascii=False, indent=2))


def main() -> None:
    for product in PRODUCTS:
        package(product)
        print(f"prepared {product['slug']}")


if __name__ == "__main__":
    main()
