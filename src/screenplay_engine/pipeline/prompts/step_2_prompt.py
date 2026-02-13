"""
Step 2 Prompt Template: Genre Classification (Save the Cat Ch.2)
Generates AI prompts to classify story into one of Blake Snyder's 10 structural genres.
"""

import hashlib
from typing import Dict, Any, List

from src.screenplay_engine.models import SnyderGenre, GENRE_DEFINITIONS


# ── Deep genre reference from Blake Snyder's Save the Cat Ch.2 ────────────
# Each genre entry contains the full working parts, structural rules,
# counter-examples (what FAILS and why), and comparable film pairings
# exactly as described in the book.

GENRE_DEEP_REFERENCE: Dict[str, Dict[str, Any]] = {
    "monster_in_the_house": {
        "book_description": (
            "Named after the most primal story ever told: 'Don't...Get...Eaten!' "
            "Can be pitched to a caveman. Can run without soundtrack and still 'get it.' "
            "The myth of the Minotaur was great (half-man/half-bull monster + maze house) "
            "but someone still came up with 'Glenn Close with a bad perm and a boiled rabbit.'"
        ),
        "working_parts_detail": {
            "monster": (
                "A MONSTER — can be supernatural OR human. Glenn Close in Fatal Attraction "
                "is a 'monster.' The monster comes 'like an avenging angel to kill those who "
                "have committed that sin and spare those who realize what that sin is.' The "
                "monster must be sufficiently threatening — 'a little spider' (Arachnophobia) "
                "is NOT scary enough because 'you step on it and it dies.'"
            ),
            "inescapable_space": (
                "A HOUSE — must be a CONFINED, inescapable space. Beach town (Jaws), spaceship "
                "(Alien), futuristic Disneyland with dinosaurs (Jurassic Park), a family unit "
                "(Fatal Attraction). The key rule: at no point can the characters simply leave. "
                "Arachnophobia FAILED because 'at any given moment, the residents can say "
                "Check please and be on the next Greyhound out of town.'"
            ),
            "sin_transgression": (
                "A SIN must be committed — 'usually greed (monetary or carnal).' The sin "
                "causally creates or summons the monster. The sin prompts the creation of "
                "a supernatural monster that comes as an avenging angel. Without the sin, "
                "the monster has no narrative justification."
            ),
            "trapped_victims": (
                "Characters are TRAPPED in the house with the monster. They cannot escape "
                "the confined space. The monster kills the sinners and spares those who "
                "recognize and atone for the sin."
            ),
            "run_and_hide_structure": (
                "'The rest is run and hide.' After the sin summons the monster and the "
                "house is established as inescapable, the story becomes an escalating "
                "pattern of running and hiding, with the monster picking off victims."
            ),
        },
        "counter_examples": [
            {
                "film": "Arachnophobia",
                "failure_reason": (
                    "BAD MONSTER: 'a little spider' — not supernatural, not scary, 'you step "
                    "on it and it dies.' NO HOUSE: 'At any given moment, the residents can say "
                    "Check please and be on the next Greyhound out of town.' Result: 'mishmash: "
                    "is it a comedy or a drama?' Violated the rules, confused the tone."
                ),
            },
        ],
        "comparable_pairings": [
            "Jaws = myth of the Minotaur = dragon slayer tales (same primal structure across millennia)",
        ],
    },
    "golden_fleece": {
        "book_description": (
            "Named after Jason and the Argonauts. All 'road movies' and quest stories. "
            "'A hero goes on the road in search of one thing and winds up discovering "
            "something else: himself.' Heist movies are a subset — any quest or 'treasure "
            "locked in a castle' approached by individual or group."
        ),
        "working_parts_detail": {
            "road_journey": (
                "The hero goes 'on the road' — a physical journey from point A to point B. "
                "This can be literal (Wizard of Oz, Road Trip) or metaphorical (Star Wars). "
                "The journey provides the structure."
            ),
            "milestones_of_growth": (
                "Milestones are people and incidents encountered along the way. 'Forcing "
                "those milestones to mean something to the hero is the job.' Whatever fun "
                "set pieces exist 'must be shaded to deliver milestones of growth for our "
                "kid lead.' Each milestone = an encounter that produces a specific internal shift."
            ),
            "external_goal_vs_self_discovery": (
                "Hero has an external goal (the fleece) that turns out less important than "
                "internal discovery. 'It's not the mileage we're racking up that makes a good "
                "Golden Fleece — it's the way the hero changes as he goes.' 'Very often the "
                "mission becomes secondary to other, more personal, discoveries.'"
            ),
            "thematic_episodes": (
                "Although 'episodic' and seemingly disconnected, incidents MUST be connected "
                "thematically by internal growth. 'It's not the incidents, it's what the hero "
                "learns about himself from those incidents that makes the story work.' If "
                "milestones don't mean something to the hero, it's just mileage."
            ),
        },
        "counter_examples": [
            {
                "film": "Generic road movies",
                "failure_reason": (
                    "If milestones don't mean something to the hero, 'it's just mileage.' "
                    "Episodes that are merely funny or exciting but don't produce internal "
                    "growth violate the genre's structural engine."
                ),
            },
        ],
        "comparable_pairings": [
            "Road Trip = Canterbury Tales (same journey structure, different era)",
            "Star Wars = Wizard of Oz (same quest-for-self-discovery engine)",
        ],
    },
    "out_of_the_bottle": {
        "book_description": (
            "Named to evoke a genie summoned from a bottle. Wish-fulfillment and "
            "comeuppance tales. Two distinct sub-types with different rules."
        ),
        "working_parts_detail": {
            "wish_or_magic": (
                "Magic enters the hero's life — can be God, a thing, a formula, luck, "
                "or divine intervention. Doesn't have to be supernatural. The magic "
                "grants the wish or imposes the curse."
            ),
            "moral_lesson": (
                "WISH sub-type: 'The hero must learn that magic isn't everything, it's "
                "better to be just like us — us members of the audience.' 'A good moral at "
                "the end must be included.' COMEUPPANCE sub-type: The jerk learns their "
                "lesson through the curse and is redeemed. 'There must be something "
                "redeemable about them.' Must include a Save the Cat scene."
            ),
            "escalating_consequences": (
                "'We don't want to see anyone, even the most underdog character succeed "
                "for too long.' The wish/curse must create escalating problems. Prolonged "
                "success without consequence violates the genre."
            ),
            "magic_source": (
                "The source of magic is irrelevant to the story mechanics — 'God, a thing, "
                "a formula, luck' — what matters is the moral lesson it forces."
            ),
        },
        "counter_examples": [],
        "comparable_pairings": [
            "Blank Check = Home Alone (wish-fulfillment kid fantasy, same engine)",
        ],
        "sub_type_details": {
            "wish_fulfillment": (
                "Hero must be 'a put-upon Cinderella who is so under the thumb of those "
                "around him that we are really rooting for anyone, or any thing, to get "
                "him a little happiness.' BUT: 'A lesson must be in the offing.' Hero "
                "learns magic isn't everything."
            ),
            "comeuppance_curse": (
                "'Here's a guy or gal who needs a swift kick in the ass.' Trickier to "
                "pull off than wish-fulfillment. 'There must be something redeemable about "
                "them.' Must include a Save the Cat scene at the outset so 'we know even "
                "though this guy or gal is a jerk, there is something in them that's worth "
                "saving.' They get 'the benefit of the magic (even though it's a curse) "
                "and triumph in the end.'"
            ),
        },
    },
    "dude_with_a_problem": {
        "book_description": (
            "'An ordinary guy finds himself in extraordinary circumstances.' Two simple "
            "components: A DUDE — 'an average guy or gal just like ourselves' — and A "
            "PROBLEM — 'something that this average guy must dig deep inside him- or "
            "herself to conquer.'"
        ),
        "working_parts_detail": {
            "ordinary_person": (
                "A DUDE — 'an average guy or gal just like ourselves.' 'The more average "
                "the guy, the bigger the challenge.' May have no super powers or skills "
                "(like Kurt Russell in Breakdown). Must be relatable, ordinary."
            ),
            "extraordinary_problem": (
                "A PROBLEM — extraordinary, overwhelming, far more powerful than the hero. "
                "'The bigger the problem, the greater the odds for our dude to overcome.' "
                "'When in doubt, make the bad guy as bad as possible. Always!' The problem "
                "must be disproportionate to the hero's abilities."
            ),
            "individuality_as_weapon": (
                "'The dude triumphs from his willingness to use his individuality to outsmart "
                "the far more powerful forces aligned against him.' Hero wins through "
                "resourcefulness and personal qualities, NOT superior force or super powers."
            ),
            "ordinary_day_disrupted": (
                "Story must begin in mundane normalcy before the extraordinary disruption "
                "arrives. The contrast between ordinary life and extraordinary problem is "
                "essential. Primal motivation is key — save the wife, save the family."
            ),
        },
        "counter_examples": [],
        "comparable_pairings": [],
    },
    "rites_of_passage": {
        "book_description": (
            "'Every change-of-life story.' Growing pain stories. 'Tales of pain and torment, "
            "but usually from an outside force — Life.' Covers puberty, mid-life crisis, "
            "old age, grieving, addiction. 'The moral of the story is always the same: "
            "That's Life!'"
        ),
        "working_parts_detail": {
            "life_transition": (
                "Every change-of-life story: puberty, mid-life crisis, old age, grieving, "
                "addiction. The transition is universal and primal — something everyone "
                "faces or will face."
            ),
            "invisible_monster": (
                "The 'monster' is 'often unseen, vague, or one which we can't get a handle "
                "on simply because we can't name it.' The monster is Life itself. Unlike "
                "Monster in the House, this monster cannot be confronted directly because "
                "it has no physical form. 'The monster sneaks up on the beleaguered hero.'"
            ),
            "pain_of_transition": (
                "'Tales of pain and torment.' The hero suffers through the transition. "
                "'Only the experience can offer a solution.' No shortcut, no cheat code — "
                "the hero must endure the full passage."
            ),
            "dramatic_irony": (
                "'Everybody's in on the joke except the person who's going through it — "
                "the story's hero.' Everyone around the hero sees what's happening, but the "
                "hero is blind to it. This creates dramatic irony that drives the story."
            ),
            "kubler_ross_stages": (
                "Structure follows Elizabeth Kubler-Ross's stages of acceptance from ON DEATH "
                "AND DYING: denial, anger, bargaining, depression, acceptance. 'These tales "
                "are about surrendering, the victory won by giving up to forces stronger than "
                "ourselves.' 'The end point is acceptance of our humanity.' 'The hero's "
                "grudging acceptance of the forces of nature that he cannot control or "
                "comprehend, and the victory comes with the hero's ability to ultimately smile.'"
            ),
        },
        "counter_examples": [],
        "comparable_pairings": [],
    },
    "buddy_love": {
        "book_description": (
            "Buddy movies AND all love stories. 'They are actually love stories in disguise. "
            "And, likewise, all love stories are just buddy movies with the potential for sex.'"
        ),
        "working_parts_detail": {
            "two_characters": (
                "Two people (or beings) whose relationship IS the story. Can be romantic "
                "partners, cop buddies, a boy and his alien (E.T.), a father and his son "
                "(Finding Nemo). The relationship drives everything."
            ),
            "hate_to_need_arc": (
                "'At first the buddies hate each other. (Where would they have to go if they "
                "didn't?)' They must start in opposition. 'Their adventure together brings "
                "out the fact that they need each other.' 'Realizing this leads to even more "
                "conflict. Who can tolerate needing anybody?'"
            ),
            "incomplete_halves": (
                "'They are, in essence, incomplete halves of a whole.' Each buddy has what "
                "the other lacks. Together they form something greater. Apart, they are "
                "diminished. This is WHY these two must be together."
            ),
            "separation_reunion": (
                "'The All Is Lost moment... is: separation, a fight, a goodbye-and-good-riddance! "
                "that is, in reality, none of these.' The separation feels final but is actually "
                "the catalyst for the reunion. 'Two people who can't stand the fact that they "
                "don't live as well without each other.'"
            ),
            "ego_surrender": (
                "Resolution requires 'surrendering their ego to win.' The buddies must give up "
                "pride, stubbornness, or self-sufficiency to accept they need the other person. "
                "Without ego surrender, the reunion cannot happen."
            ),
        },
        "counter_examples": [],
        "comparable_pairings": [
            "Point Break = Fast and Furious (beat for beat same movie, surfing vs. cars)",
        ],
        "sub_type_details": {
            "catalyst_buddy": (
                "Often one buddy is the hero (does all/most changing) while the other is the "
                "catalyst (does slight/no changing). Rain Man: Tom Cruise is hero, Dustin "
                "Hoffman is catalyst. Lethal Weapon: Danny Glover is hero (his story/"
                "transformation), Mel Gibson is catalyst. 'A being comes into one's life, "
                "affects it, and leaves.' Many 'boy and his dog' tales are this — including E.T."
            ),
        },
    },
    "whydunit": {
        "book_description": (
            "'Who cares who?, it's why? that counts.' The darkest genre — walks 'on the dark "
            "side,' takes us 'to the shadowy part of the street.'"
        ),
        "working_parts_detail": {
            "mystery": (
                "A mystery that compels investigation. But the mystery is not about WHO did "
                "it — 'Who cares who?' — it's about WHY. The real mystery is about human "
                "nature, not clues and suspects."
            ),
            "investigation": (
                "An investigation that peels back layers of human darkness. 'Like Citizen "
                "Kane... the story is about seeking the innermost chamber of the human heart "
                "and discovering something unexpected, something dark and often unattractive.'"
            ),
            "dark_revelation": (
                "The investigation reveals a dark truth about human nature. 'It turns the "
                "X-ray machine back on ourselves and asks: Are we this evil?' The revelation "
                "must implicate not just the characters but the audience's own nature."
            ),
            "audience_surrogate": (
                "'We in the audience are the detectives, ultimately.' We have 'a surrogate "
                "or surrogates onscreen doing the work for us.' 'It's we who must ultimately "
                "sift through the information, and we who must be shocked by what we find.' "
                "This is NOT about the hero changing — 'it's about the audience discovering "
                "something about human nature they did not think was possible.'"
            ),
        },
        "counter_examples": [],
        "comparable_pairings": [
            "Who Framed Roger Rabbit = Chinatown (same Whydunit engine, different tone)",
        ],
    },
    "fool_triumphant": {
        "book_description": (
            "'On the outside, he's just the Village Idiot, but further examination reveals "
            "him to be the wisest among us.' 'Watching a so-called idiot get the goat of "
            "those society deems to be the winners in life gives us all hope, and pokes fun "
            "at the structures we take so seriously.'"
        ),
        "working_parts_detail": {
            "underdog_fool": (
                "An UNDERDOG — 'seemingly so inept and so unequipped for life that everyone "
                "around him discounts his odds for success (and does so repeatedly in the "
                "set-up).' The fool appears stupid but is actually the wisest. The setup "
                "must REPEATEDLY show others discounting the Fool's chances."
            ),
            "powerful_institution": (
                "An INSTITUTION for the underdog to attack. 'Set the underdog Fool against "
                "a bigger, more powerful, and often establishment bad guy.' The institution "
                "represents the serious, powerful forces of society."
            ),
            "insider_accomplice": (
                "Often an INSIDER ACCOMPLICE — 'who is in on the joke and can't believe the "
                "Fool is getting away with his ruse.' Examples: Salieri in Amadeus, The Doctor "
                "in Being There, Lieutenant Dan in Forrest Gump, Herbert Lom in The Pink "
                "Panther. The accomplice 'often gets the brunt of the slapstick' and "
                "'ultimately gets the pie in the face.' 'Their crime is being close to the "
                "idiot, seeing him for what he really is, and being stupid enough to try "
                "to interfere.'"
            ),
        },
        "counter_examples": [],
        "comparable_pairings": [],
    },
    "institutionalized": {
        "book_description": (
            "'Stories about groups, institutions and families.' 'Both honor the institution "
            "and expose the problems of losing one's identity to it.' 'When we put on a "
            "uniform... we give up who we are to a certain extent.' 'About the pros and cons "
            "of putting the group ahead of ourselves.'"
        ),
        "working_parts_detail": {
            "group": (
                "A GROUP, institution, or 'family' that has its own rules, culture, and "
                "identity. The group dynamic 'is often crazy and even self-destructive.' "
                "'Suicide is painless' (theme of MASH) 'isn't so much about the insanity of "
                "war as the insanity of the herd mentality.'"
            ),
            "newcomer": (
                "Often told from POV of a NEWCOMER — 'He is us — a virgin who is new to this "
                "group.' Jane Fonda in 9 to 5, Tom Hulce in Animal House. Newcomers can ask "
                "'How does that work?' — invaluable relayers of exposition. The newcomer is "
                "the audience's way into the strange world of the group."
            ),
            "cost_of_belonging": (
                "The story explores the cost of belonging to the group. 'When we put on a "
                "uniform... we give up who we are to a certain extent.' What do you sacrifice "
                "to belong? The story must both honor the institution's value AND expose the "
                "problems of losing identity to it."
            ),
            "breakout_character": (
                "Each has 'a breakout character whose role it is to expose the group goal as "
                "a fraud' — Jack Nicholson (Cuckoo's Nest), Kevin Spacey (American Beauty), "
                "Donald Sutherland (MASH), Al Pacino (Godfather). The breakout character sees "
                "through the institution's facade."
            ),
            "experienced_guide": (
                "An experienced member who shows the newcomer the ropes and helps the audience "
                "understand how the institution works. Provides context for the group's norms "
                "and contradictions."
            ),
        },
        "counter_examples": [],
        "comparable_pairings": [],
        "thematic_through_line": (
            "Ultimate question: 'Who's crazier, me or them?' Al Pacino's face at end of "
            "Godfather 2, Kevin Spacey's discovery in American Beauty, Jack Nicholson's "
            "blank post-operative expression in Cuckoo's Nest — 'Because it's the same "
            "movie, with the same message, told in extremely different and moving ways.'"
        ),
    },
    "superhero": {
        "book_description": (
            "Exact OPPOSITE of Dude With A Problem. 'An extraordinary person finds himself "
            "in an ordinary world.' Goes beyond guys in capes: includes human superheroes "
            "challenged by mediocre world (Gladiator, A Beautiful Mind). 'Ultimately, all "
            "superhero tales are about being different.'"
        ),
        "working_parts_detail": {
            "extraordinary_being": (
                "An extraordinary person — supernatural powers, genius intellect, or simply "
                "extraordinary character. 'Born into a world he did not create.' Goes beyond "
                "literal superheroes to include Gladiator, A Beautiful Mind, Frankenstein, "
                "Dracula."
            ),
            "ordinary_world": (
                "The ordinary world that cannot understand or accept the extraordinary being. "
                "The contrast between the hero's gifts and the mundane world creates the "
                "central tension."
            ),
            "jealous_mediocrity": (
                "'The Superhero must deal with those who are jealous of his unique point of "
                "view and superior mind.' The antagonist is not a rival superhero but the "
                "jealousy and mediocrity of ordinary people — tiny minds who resent greatness."
            ),
            "creation_myth": (
                "'The creation myth that begins each Superhero franchise stresses sympathy for "
                "the Superhero's plight.' Must establish sympathy through 'the pain that goes "
                "hand-in-hand with having these advantages.' 'It's not easy being Bruce Wayne. "
                "He's tortured!' Bruce Wayne is 'admirable because he eschews his personal "
                "comfort in the effort to give back to the community.' 'Our identification "
                "with him must come from sympathy for the plight of being misunderstood.'"
            ),
        },
        "counter_examples": [
            {
                "film": "Robocop 2",
                "failure_reason": (
                    "'Once established, filmmakers forget to re-create that sympathy' — why "
                    "Robocop 2 fails. The creation myth that begins each Superhero franchise "
                    "stresses sympathy for the Superhero's plight. In sequels, this sympathy "
                    "must be RE-CREATED, not assumed. Robocop 2 forgot this rule."
                ),
            },
        ],
        "comparable_pairings": [
            "Superman = Hercules (same extraordinary-being-in-ordinary-world engine across millennia)",
            "The Matrix = Monsters Inc. ('Yup. Same movie.' — Blake Snyder)",
        ],
    },
}


class Step2Prompt:
    """Prompt generator for Step 2: Genre Classification"""

    VERSION = "2.0.0"

    SYSTEM_PROMPT = (
        "You are a Save the Cat! genre classification expert. "
        "Classify stories into Blake Snyder's 10 structural genres.\n\n"
        "Blake insists: 'Movies are intricately made emotion machines. They are Swiss watches "
        "of precise gears and spinning wheels. You have to be able to take them apart and put "
        "them back together again. In the dark. In your sleep.'\n\n"
        "The 10 genres are:\n\n"
        "1. MONSTER IN THE HOUSE (monster_in_the_house)\n"
        "   Films: Jaws, Alien, The Exorcist, Fatal Attraction, Panic Room, Jurassic Park, Tremors\n"
        "   Working Parts:\n"
        "   - A MONSTER: supernatural or human (Glenn Close with a bad perm counts). Must be "
        "sufficiently threatening — comes 'like an avenging angel' to punish the sin.\n"
        "   - A HOUSE: MUST be a confined, inescapable space — beach town, spaceship, futuristic "
        "Disneyland with dinosaurs, a family unit. Characters CANNOT simply leave.\n"
        "   - A SIN: Usually greed (monetary or carnal). The sin causally CREATES or summons the "
        "monster. Without the sin, no narrative justification for the monster.\n"
        "   - Monster kills sinners, spares those who realize and atone for the sin.\n"
        "   - Structure is 'run and hide' — escalating chase within the confined space.\n"
        "   - Can be pitched to a caveman: 'Don't...Get...Eaten!'\n"
        "   FAILURE: Arachnophobia — bad monster ('a little spider, you step on it and it dies'), "
        "no house ('residents can be on the next Greyhound out of town'). Result: confused tone.\n\n"
        "2. GOLDEN FLEECE (golden_fleece)\n"
        "   Films: Star Wars, Wizard of Oz, Planes Trains and Automobiles, Back to the Future, "
        "Road Trip, Ocean's Eleven, Dirty Dozen, Magnificent Seven\n"
        "   Working Parts:\n"
        "   - A ROAD JOURNEY/QUEST: Hero goes 'on the road' in search of one thing, discovers himself.\n"
        "   - MILESTONES OF GROWTH: People and incidents encountered along the way. Each milestone "
        "must produce a specific internal shift. 'Forcing those milestones to mean something to "
        "the hero is the job.'\n"
        "   - EXTERNAL GOAL vs. SELF-DISCOVERY: The fleece (external goal) turns out less important "
        "than what the hero learns about himself.\n"
        "   - THEMATIC EPISODES: Although episodic, incidents MUST be thematically connected. "
        "'It's not the mileage — it's the way the hero changes as he goes.'\n"
        "   - Heist movies are a subset: the 'mission' becomes secondary to personal discoveries.\n"
        "   FAILURE: If milestones don't mean something to the hero, 'it's just mileage.'\n\n"
        "3. OUT OF THE BOTTLE (out_of_the_bottle)\n"
        "   Films: Blank Check, Bruce Almighty, The Mask, Liar Liar, Freaky Friday, Groundhog Day, "
        "Love Potion #9, Flubber\n"
        "   Working Parts:\n"
        "   - WISH OR MAGIC: Magic enters the hero's life (God, thing, formula, luck — source "
        "doesn't matter).\n"
        "   - TWO DISTINCT SUB-TYPES:\n"
        "     a) WISH-FULFILLMENT: Hero is 'a put-upon Cinderella so under the thumb of those "
        "around him that we are really rooting for any thing to get him a little happiness.' BUT: "
        "'A lesson must be in the offing.' 'Hero must learn that magic isn't everything, it's "
        "better to be just like us.' 'A good moral at the end must be included.'\n"
        "     b) COMEUPPANCE: 'A guy or gal who needs a swift kick in the ass.' Gets cursed. "
        "'Must include a Save the Cat scene' — 'even though this guy is a jerk, there is something "
        "worth saving.' Trickier than wish-fulfillment. They triumph through the curse.\n"
        "   - ESCALATING CONSEQUENCES: 'We don't want to see anyone succeed for too long.' "
        "Prolonged success without consequence violates the genre.\n"
        "   - MORAL LESSON: Always required at end.\n\n"
        "4. DUDE WITH A PROBLEM (dude_with_a_problem)\n"
        "   Films: Die Hard, Schindler's List, The Terminator, Titanic, Breakdown\n"
        "   Working Parts:\n"
        "   - An ORDINARY PERSON: 'An average guy or gal just like ourselves.' The more average "
        "the person, the bigger the challenge should be.\n"
        "   - An EXTRAORDINARY PROBLEM: Far more powerful than the hero. 'When in doubt, make the "
        "bad guy as bad as possible. Always!'\n"
        "   - INDIVIDUALITY AS WEAPON: 'The dude triumphs from his willingness to use his "
        "individuality to outsmart the far more powerful forces.' Wins through resourcefulness, "
        "NOT superior force or super powers.\n"
        "   - ORDINARY DAY DISRUPTED: Must begin in mundane normalcy before extraordinary disruption.\n"
        "   - PRIMAL MOTIVATION: Stakes must be personal/domestic — save the wife, save the family.\n\n"
        "5. RITES OF PASSAGE (rites_of_passage)\n"
        "   Films: 10 (Dudley Moore), Ordinary People, Days of Wine and Roses, Lost Weekend, "
        "28 Days, When a Man Loves a Woman\n"
        "   Working Parts:\n"
        "   - A LIFE TRANSITION: puberty, mid-life crisis, old age, grieving, addiction.\n"
        "   - An INVISIBLE MONSTER: 'Often unseen, vague, or one which we can't get a handle on "
        "simply because we can't name it.' The monster is Life itself. Cannot be confronted directly.\n"
        "   - DRAMATIC IRONY: 'Everybody's in on the joke except the person going through it — "
        "the story's hero.' Everyone sees it except the hero.\n"
        "   - KUBLER-ROSS STAGES: Structure follows denial, anger, bargaining, depression, "
        "acceptance. 'These tales are about surrendering, the victory won by giving up to forces "
        "stronger than ourselves.'\n"
        "   - Victory = SURRENDER and ACCEPTANCE, not conquest. 'The end point is acceptance of "
        "our humanity.' 'Only the experience can offer a solution.'\n"
        "   - Moral is always: 'That's Life!'\n\n"
        "6. BUDDY LOVE (buddy_love)\n"
        "   Films: Butch Cassidy and the Sundance Kid, 48 Hours, Thelma & Louise, Finding Nemo, "
        "Rain Man, Lethal Weapon, E.T., How to Lose a Guy in 10 Days, Wayne's World\n"
        "   Working Parts:\n"
        "   - TWO CHARACTERS whose relationship IS the story. 'Buddy movies are just love stories "
        "in disguise. And all love stories are just buddy movies with the potential for sex.'\n"
        "   - HATE-TO-NEED ARC: 'At first the buddies hate each other. (Where would they have to "
        "go if they didn't?)' Adventure reveals they need each other. 'Realizing this leads to "
        "even more conflict. Who can tolerate needing anybody?'\n"
        "   - INCOMPLETE HALVES: 'They are, in essence, incomplete halves of a whole.'\n"
        "   - SEPARATION/REUNION: All Is Lost = 'separation, a fight, a goodbye-and-good-riddance "
        "that is, in reality, none of these.'\n"
        "   - EGO SURRENDER: Must 'surrender their ego to win.'\n"
        "   - CATALYST BUDDY subset: One buddy changes (hero), other catalyzes. Rain Man: Tom Cruise "
        "= hero, Dustin Hoffman = catalyst. E.T.: 'A being comes into one's life, affects it, "
        "and leaves.'\n\n"
        "7. WHYDUNIT (whydunit)\n"
        "   Films: Chinatown, China Syndrome, All the President's Men, JFK, The Insider, "
        "Citizen Kane\n"
        "   Working Parts:\n"
        "   - 'Who cares who? — it's WHY that counts.'\n"
        "   - NOT about hero changing — 'about the audience discovering something about human "
        "nature they did not think was possible.'\n"
        "   - AUDIENCE IS THE REAL DETECTIVE: 'We in the audience are the detectives, ultimately.' "
        "Onscreen character is our surrogate doing the work for us.\n"
        "   - DARK REVELATION: 'Seeking the innermost chamber of the human heart and discovering "
        "something unexpected, dark, and often unattractive.' 'Turns the X-ray machine back on "
        "ourselves and asks: Are we this evil?'\n"
        "   - Takes us 'to the shadowy part of the street.'\n\n"
        "8. FOOL TRIUMPHANT (fool_triumphant)\n"
        "   Films: Chaplin/Keaton/Lloyd films, Dave, Being There, Amadeus, Forrest Gump, The Jerk, "
        "Charly, Awakenings, The Pink Panther\n"
        "   Working Parts:\n"
        "   - An UNDERDOG FOOL: 'Seemingly so inept and so unequipped for life that everyone "
        "discounts his odds for success (and does so REPEATEDLY in the set-up).' On the outside, "
        "Village Idiot; further examination reveals wisest among us.\n"
        "   - A POWERFUL INSTITUTION: 'Set the underdog Fool against a bigger, more powerful, and "
        "often establishment bad guy.'\n"
        "   - An INSIDER ACCOMPLICE: 'In on the joke and can't believe the Fool is getting away "
        "with his ruse.' Examples: Salieri (Amadeus), the Doctor (Being There), Lt. Dan (Forrest "
        "Gump), Herbert Lom (Pink Panther). The accomplice 'often gets the brunt of the slapstick' "
        "and 'ultimately gets the pie in the face.' 'Their crime is being close to the idiot, "
        "seeing him for what he really is, and being stupid enough to try to interfere.'\n\n"
        "9. INSTITUTIONALIZED (institutionalized)\n"
        "   Films: One Flew Over the Cuckoo's Nest, American Beauty, MASH, The Godfather, "
        "Animal House, 9 to 5\n"
        "   Working Parts:\n"
        "   - A GROUP/INSTITUTION/'FAMILY' with its own rules and culture.\n"
        "   - A NEWCOMER: 'He is us — a virgin who is new to this group.' (Jane Fonda in 9 to 5, "
        "Tom Hulce in Animal House.) Can ask 'How does that work?' — invaluable exposition device.\n"
        "   - A BREAKOUT CHARACTER: 'Whose role it is to expose the group goal as a fraud.' "
        "(Nicholson, Spacey, Sutherland, Pacino.) Sees through the institution's facade.\n"
        "   - Story must BOTH honor the institution AND expose the problems of losing identity to it.\n"
        "   - 'When we put on a uniform... we give up who we are to a certain extent.'\n"
        "   - 'Suicide is painless' (MASH theme) is about insanity of herd mentality.\n"
        "   - Ultimate question: 'Who's crazier, me or them?'\n\n"
        "10. SUPERHERO (superhero)\n"
        "   Films: Superman, Batman, Gladiator, A Beautiful Mind, Frankenstein, Dracula, X-Men, "
        "Robocop\n"
        "   Working Parts:\n"
        "   - EXACT OPPOSITE of Dude With A Problem: extraordinary person in ordinary world.\n"
        "   - An EXTRAORDINARY BEING: supernatural powers, genius, or extraordinary character. "
        "Goes beyond capes — Gladiator, A Beautiful Mind, Frankenstein are all Superhero.\n"
        "   - JEALOUS MEDIOCRITY: 'Must deal with those who are jealous of his unique point of "
        "view and superior mind.' Nemesis is mediocrity, not a rival superhero.\n"
        "   - CREATION MYTH: 'Stresses sympathy for the Superhero's plight.' Must create sympathy "
        "through 'the pain that goes with having these advantages.' 'It's not easy being Bruce "
        "Wayne. He's tortured!' 'Our identification must come from sympathy for the plight of "
        "being misunderstood.'\n"
        "   - 'Ultimately, all superhero tales are about being different.'\n"
        "   FAILURE: Robocop 2 — 'filmmakers forget to re-create that sympathy' in sequels.\n\n"
        "COMPARABLE FILM PAIRINGS (Blake Snyder says these are 'the same movie'):\n"
        "  - Point Break = Fast and Furious (beat for beat, surfing vs. cars)\n"
        "  - The Matrix = Monsters Inc. ('Yup. Same movie.')\n"
        "  - Superman = Hercules (same engine across millennia)\n"
        "  - Who Framed Roger Rabbit = Chinatown (same Whydunit engine)\n"
        "  - Blank Check = Home Alone (same wish-fulfillment kid fantasy)\n"
        "  - Road Trip = Canterbury Tales (same journey structure)\n"
        "  - Jaws = myth of the Minotaur = dragon slayer tales\n\n"
        "Snyder warns about borderline cases:\n"
        "  - Breakfast Club: Rites of Passage (NOT Institutionalized)\n"
        "  - Rain Man: Buddy Love (NOT Golden Fleece)\n"
        "  - Zoolander: Superhero\n"
        "When in doubt, ask: what is the STRUCTURAL ENGINE of this story?\n\n"
        "'True originality can't begin until you know what you're breaking away from.'\n\n"
        "You MUST respond with valid JSON only. No markdown, no commentary."
    )

    USER_PROMPT_TEMPLATE = """Classify this story into exactly ONE of Blake Snyder's 10 structural genres.

LOGLINE:
{logline}

TITLE:
{title}

SNOWFLAKE SYNOPSIS:
{synopsis}

INSTRUCTIONS:
1. Classify into exactly ONE genre from: monster_in_the_house, golden_fleece, out_of_the_bottle, dude_with_a_problem, rites_of_passage, buddy_love, whydunit, fool_triumphant, institutionalized, superhero
2. Your working_parts array MUST contain one entry for EACH part_name listed below for your chosen genre. Use these EXACT part_name values:
   - monster_in_the_house: monster, inescapable_space, sin_transgression, trapped_victims, run_and_hide_structure (5 entries)
   - golden_fleece: road_journey, milestones_of_growth, external_goal_vs_self_discovery, thematic_episodes (4 entries)
   - out_of_the_bottle: wish_or_magic, moral_lesson, escalating_consequences, magic_source (4 entries)
   - dude_with_a_problem: ordinary_person, extraordinary_problem, individuality_as_weapon, ordinary_day_disrupted (4 entries)
   - rites_of_passage: life_transition, invisible_monster, pain_of_transition, dramatic_irony, kubler_ross_stages (5 entries)
   - buddy_love: two_characters, hate_to_need_arc, incomplete_halves, separation_reunion, ego_surrender (5 entries)
   - whydunit: mystery, investigation, dark_revelation, audience_surrogate (4 entries)
   - fool_triumphant: underdog_fool, powerful_institution, insider_accomplice (3 entries)
   - institutionalized: group, newcomer, cost_of_belonging, breakout_character, experienced_guide (5 entries)
   - superhero: extraordinary_being, ordinary_world, jealous_mediocrity, creation_myth (4 entries)
3. List the genre's structural rules and constraints that this screenplay must follow
4. State the core question the genre asks of the audience
5. Identify the "twist" — what makes this story "the same thing, only different" from other films in this genre. Reference a SPECIFIC convention you are subverting.
6. List audience conventions and expectations for this genre
7. RUNNER-UP: What genre was your second choice? Why did you eliminate it? (Snyder says borderline cases are where writers get lost.)
8. COMPARABLE FILMS: Name 3-5 films in the same genre that this story is most like. State the lineage — "what movie begat what."
9. If the genre has sub-types (e.g. Out of the Bottle has wish-fulfillment vs. comeuppance), identify which sub-type this story is.

GENRE REFERENCE:
{genre_reference}

OUTPUT FORMAT (JSON):
{{
    "genre": "<one of the 10 genre values>",
    "sub_type": "<specific sub-type if applicable, e.g. 'comeuppance_curse', 'catalyst_buddy', or null if genre has no sub-types>",
    "working_parts": [
        {{
            "part_name": "<working part name matching genre definition>",
            "story_element": "<2+ sentences: how this part manifests in THIS story>"
        }}
    ],
    "rules": [
        "<specific structural rule for this genre — how it constrains THIS screenplay>",
        "<another rule — be specific to this story, not generic>"
    ],
    "core_question": "<the central question this genre asks of the audience>",
    "twist": "<what SPECIFIC convention are you subverting, and how? Reference the genre tradition.>",
    "conventions": [
        "<audience expectation 1>",
        "<audience expectation 2>"
    ],
    "genre_justification": "<1-2 sentences explaining why this genre fits best>",
    "runner_up_genre": "<second-choice genre>",
    "runner_up_elimination": "<why the runner-up was eliminated — what structural element disqualifies it?>",
    "comparable_films": [
        "<film 1 in same genre that this story resembles>",
        "<film 2>",
        "<film 3>"
    ]
}}"""

    REVISION_PROMPT_TEMPLATE = """Your previous genre classification had validation errors. Fix them.

PREVIOUS RESPONSE:
{previous_response}

VALIDATION ERRORS:
{errors}

FIX SUGGESTIONS:
{suggestions}

LOGLINE:
{logline}

TITLE:
{title}

SNOWFLAKE SYNOPSIS:
{synopsis}

Provide a corrected JSON response that fixes ALL listed errors.
Respond with valid JSON only. No markdown, no commentary."""

    def _build_genre_reference(self) -> str:
        """Build a formatted reference of all genre definitions with deep book content."""
        lines = []
        for genre, definition in GENRE_DEFINITIONS.items():
            genre_key = genre.value
            deep = GENRE_DEEP_REFERENCE.get(genre_key, {})

            lines.append(f"  {genre_key}:")
            # Book description (deep context from Ch.2)
            if deep.get("book_description"):
                lines.append(f"    Book context: {deep['book_description']}")
            lines.append(f"    Working parts: {', '.join(definition['working_parts'])}")
            # Deep working-part descriptions
            if deep.get("working_parts_detail"):
                for part_name, detail in deep["working_parts_detail"].items():
                    lines.append(f"      {part_name}: {detail}")
            lines.append(f"    Core question: {definition['core_question']}")
            lines.append(f"    Core rule: {definition['core_rule']}")
            if definition.get("sub_types"):
                lines.append(f"    Sub-types: {', '.join(definition['sub_types'])}")
            # Deep sub-type descriptions
            if deep.get("sub_type_details"):
                for st_name, st_detail in deep["sub_type_details"].items():
                    lines.append(f"      {st_name}: {st_detail}")
            if definition.get("example_films"):
                lines.append(f"    Example films: {', '.join(definition['example_films'][:5])}")
            if definition.get("rules"):
                for i, rule in enumerate(definition["rules"][:3], 1):
                    lines.append(f"    Rule {i}: {rule}")
            # Counter-examples (what FAILS and why)
            if deep.get("counter_examples"):
                for ce in deep["counter_examples"]:
                    lines.append(f"    COUNTER-EXAMPLE: {ce['film']} — {ce['failure_reason']}")
            # Comparable film pairings
            if deep.get("comparable_pairings"):
                for cp in deep["comparable_pairings"]:
                    lines.append(f"    COMPARABLE PAIRING: {cp}")
            # Thematic through-line (for institutionalized)
            if deep.get("thematic_through_line"):
                lines.append(f"    Thematic through-line: {deep['thematic_through_line']}")
            lines.append("")
        return "\n".join(lines)

    def generate_prompt(
        self,
        step_1_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate the full prompt for Step 2 genre classification.

        Args:
            step_1_artifact: The validated Step 1 logline artifact.
            snowflake_artifacts: Snowflake pipeline outputs (synopsis data).

        Returns:
            Dict with system and user prompts plus metadata.
        """
        # Validate required inputs — no silent fallbacks
        logline = step_1_artifact.get("logline")
        if not logline:
            raise ValueError("Step 1 artifact is missing required field: 'logline'")
        title = step_1_artifact.get("title")
        if not title:
            raise ValueError("Step 1 artifact is missing required field: 'title'")

        # Extract synopsis from snowflake artifacts (try step_4 first, then step_2, then step_1)
        synopsis = ""
        if "step_4" in snowflake_artifacts:
            synopsis = snowflake_artifacts["step_4"].get(
                "one_page_synopsis",
                snowflake_artifacts["step_4"].get("synopsis", ""),
            )
        elif "step_2" in snowflake_artifacts:
            synopsis = snowflake_artifacts["step_2"].get(
                "paragraph_summary",
                snowflake_artifacts["step_2"].get("summary", ""),
            )

        if not synopsis and "step_1" in snowflake_artifacts:
            synopsis = snowflake_artifacts["step_1"].get("logline", "")

        if not synopsis:
            raise ValueError("No synopsis found in Snowflake artifacts (checked step_4, step_2, step_1)")

        genre_reference = self._build_genre_reference()

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            logline=logline,
            title=title,
            synopsis=synopsis,
            genre_reference=genre_reference,
        )

        # Calculate prompt hash for tracking
        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }

    def generate_revision_prompt(
        self,
        previous_response: Dict[str, Any],
        validation_errors: List[str],
        fix_suggestions: List[str],
        step_1_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate a revision prompt to fix validation errors.

        Args:
            previous_response: The artifact that failed validation.
            validation_errors: List of validation error strings.
            fix_suggestions: List of fix suggestion strings.
            step_1_artifact: The Step 1 logline artifact.
            snowflake_artifacts: Snowflake pipeline outputs.

        Returns:
            Dict with system and user prompts plus metadata.
        """
        import json

        logline = step_1_artifact.get("logline")
        if not logline:
            raise ValueError("Step 1 artifact is missing 'logline' for revision")
        title = step_1_artifact.get("title", "")

        synopsis = ""
        if "step_4" in snowflake_artifacts:
            synopsis = snowflake_artifacts["step_4"].get(
                "one_page_synopsis",
                snowflake_artifacts["step_4"].get("synopsis", ""),
            )
        elif "step_2" in snowflake_artifacts:
            synopsis = snowflake_artifacts["step_2"].get(
                "paragraph_summary",
                snowflake_artifacts["step_2"].get("summary", ""),
            )

        error_text = "\n".join(f"- {e}" for e in validation_errors)
        suggestion_text = "\n".join(f"- {s}" for s in fix_suggestions)

        user_prompt = self.REVISION_PROMPT_TEMPLATE.format(
            previous_response=json.dumps(previous_response, indent=2),
            errors=error_text,
            suggestions=suggestion_text,
            logline=logline,
            title=title,
            synopsis=synopsis or logline,
        )

        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
            "revision": True,
        }
