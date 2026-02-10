"""
Save the Cat: Superhero Genre Definition
Extracted from "Save the Cat Goes to the Movies" by Blake Snyder
Chapter 10: Superhero (pages 257-281)
"""

SUPERHERO_GENRE = {
    "genre_name": "Superhero",
    "abbreviation": "SH",
    "definition": (
        "A story about a special being — imbued with extraordinary power or a mission to be super — "
        "who descends from 'Mt. Olympus' to save ordinary people, but pays a heavy personal price for being special. "
        "Not quite human nor quite god, the Superhero bears the hostility, jealousy, and fear of the very people he saves. "
        "These are stories of triumph AND sacrifice. The hero knows he is special and will pay a price for being so."
    ),
    "required_components": {
        "power": (
            "A special 'power' the hero is imbued with, or a mission to be 'super' that makes him more than human. "
            "At first the power seems like fun — Superman testing his speed, Spidey flinging webs, Jesus healing the lame. "
            "We watch the special being show off his specialness. But for every superpower, there is a cosmic payback coming."
        ),
        "nemesis": (
            "An equally powerful bad guy — the Nemesis — who opposes the hero's rise. "
            "The Nemesis is often a 'super genius' relying on his brain (symbol of self-will run amok). "
            "What separates hero from Nemesis is FAITH: the Superhero knows he is the chosen one; "
            "the Nemesis secretly knows his claim is false and must kill the real chosen one to triumph. "
            "The distinction between good and evil is slight — these are the most fascinating match-ups in storytelling. "
            "Examples: Lex Luthor/Superman, Moriarty/Holmes, Commodus/Maximus, Scar/Simba, Doc Ock/Spider-Man, Agent Smith/Neo."
        ),
        "curse": (
            "A 'curse' or Achilles heel — for every power there is a defect the bad guy can exploit. "
            "The curse balances the powers and makes us not hate the protagonist. "
            "Includes: sexual sacrifice (Jake La Motta, Peter Parker, Clark Kent), hidden identity burden, "
            "kryptonite for Superman, daylight for Dracula, full moon for Wolfman. "
            "The hero is also cursed by us — like Gulliver tied down by a thousand Lilliputian threads. "
            "Being special means giving something up."
        ),
    },
    "key_distinctions_from_fool_triumphant": (
        "Both share the 'hero changes his name' beat, but in FT the name is a disguise to sneak into Act Two, "
        "while in SH the hero PROCLAIMS his new name (El Aurens, Gladiator, like Abram becoming Abraham). "
        "A Fool is unaware of his power's cost and sometimes unaware he is opposed. "
        "A Superhero knows power comes with a price and faces a Nemesis with matching or greater abilities."
    ),
    "recurring_character_mascot": (
        "The Mascot: a loyal, very human underling who looks up to the hero but can never be him. "
        "Examples: Jimmy Olsen in Superman, Joey (brother) in Raging Bull, Timon in The Lion King, "
        "Mouse in The Matrix, Lawrence's chosen servants in Lawrence of Arabia. "
        "Often used by the Nemesis to threaten the Superhero."
    ),
    "recurring_beat_crucifixion": (
        "A 'crucifixion' beat appears across nearly ALL Superhero stories: the hero is tortured, "
        "broken, or killed for his trouble. Jake La Motta's bloody beating on the ropes, "
        "Neo dying and being reborn by Trinity's kiss, Maximus stabbed before the final duel, "
        "Spider-Man stopping the train with arms outstretched. This echoes the Christ archetype at the genre's root."
    ),
    "recurring_beat_faith_vs_self_will": (
        "SH tales are fundamentally about faith. The hero surrenders control to an unseen power to become great. "
        "The Nemesis relies on self-will, brains, and machinations — self-will run amok. "
        "If the Nemesis were truly special, he would not need to kill anyone."
    ),
    "sub_types": {
        "peoples_superhero": {
            "description": "A civilian rising from the ranks to meet a great challenge.",
            "examples": ["Gladiator", "Robin Hood", "Zorro", "Ben-Hur", "Spartacus"],
            "cousins": [
                "Gunga Din", "Ben-Hur", "High Plains Drifter", "Greystoke: The Legend of Tarzan",
                "The Three Musketeers", "Robin Hood: Prince of Thieves", "The Mask of Zorro",
                "Whale Rider", "The Patriot", "Casino Royale",
            ],
        },
        "comic_book_superhero": {
            "description": "The classic powered hero from comics, often with 'Man' in the name.",
            "examples": ["Spider-Man 2", "Superman", "Batman", "X-Men"],
            "cousins": [
                "Batman", "The Fantastic Four", "The Incredibles", "X-Men",
                "Blade", "The Hulk", "Tank Girl", "Catwoman", "The Crow", "Hellboy",
            ],
        },
        "real_life_superhero": {
            "description": "True tales of biography shaped into the Superhero form — special people who paid the price.",
            "examples": ["Raging Bull", "Gandhi", "Joan of Arc", "Lawrence of Arabia"],
            "cousins": [
                "Lenny", "Gandhi", "Braveheart", "Malcolm X", "Frances",
                "Joan of Arc", "Erin Brockovich", "The Passion of the Christ",
                "The Aviator", "A Beautiful Mind",
            ],
        },
        "fantasy_superhero": {
            "description": "Savior tales set in a made-up world with little historic context.",
            "examples": ["The Matrix", "Crouching Tiger Hidden Dragon"],
            "cousins": [
                "Brazil", "Hook", "The Neverending Story", "MirrorMask",
                "The Nightmare Before Christmas", "Antz",
                "The League of Extraordinary Gentlemen", "Van Helsing",
                "V for Vendetta", "Eragon",
            ],
        },
        "storybook_superhero": {
            "description": "Animated 'chosen one' legends made palpable with funny songs and talking animals.",
            "examples": ["The Lion King", "Mulan"],
            "cousins": [
                "Peter Pan", "The Hunchback of Notre Dame", "Mulan",
                "The Chronicles of Narnia: The Lion the Witch and the Wardrobe",
                "The Jungle Book", "The Little Mermaid",
                "Willy Wonka & the Chocolate Factory", "Harry Potter series",
                "Happy Feet", "Ratatouille",
            ],
        },
    },
    "bs2_beats": {
        "opening_image": {
            "beat_number": 1,
            "superhero_manifestation": (
                "Establishes the hero's current state — often BEFORE the power, or in a fallen/diminished condition "
                "that bookends the Final Image: Jake La Motta fat and rehearsing alone (1964), Simba's birth on Pride Rock, "
                "a cryptic phone call about 'The One' on a computer screen, Maximus dreaming of home touching wheat, "
                "Peter Parker late for work ogling MJ on a billboard."
            ),
        },
        "theme_stated": {
            "beat_number": 2,
            "superhero_manifestation": (
                "Someone voices the core tension of being special — the price of power, the meaning of duty: "
                "'What are you trying to prove?' (Raging Bull), 'There's more to being King than getting your way' (Lion King), "
                "'Are you awake or dreaming?' (Matrix), 'People should know when they're conquered' (Gladiator), "
                "'A promise means nothing' (Spider-Man 2). The theme foreshadows that the hero's gift will exact a toll."
            ),
        },
        "set_up": {
            "beat_number": 3,
            "superhero_manifestation": (
                "We see the hero's world before transformation and the 'six things that need fixing': "
                "the loveless marriage and underdog status (Raging Bull), the cocky young cub with a powerful father (Lion King), "
                "the slacker hacker told 'you are my savior' (Matrix), the fearless general amid political vipers (Gladiator), "
                "the multi-tasking hell of juggling identity and duty (Spider-Man 2). "
                "The Nemesis is introduced or hinted at, and the Mascot appears."
            ),
        },
        "catalyst": {
            "beat_number": 4,
            "superhero_manifestation": (
                "An external event ignites the hero's path toward super-ness or introduces the force that will oppose him: "
                "Jake sees Vickie and is smitten — she will fuel his desire to win; Scar uses Simba's disobedience to plot a coup; "
                "a mysterious phone from Morpheus arrives at Neo's workplace; the Emperor asks Maximus to succeed him "
                "and Commodus murders the father; Peter meets Doc Octavius, who has balanced normalcy and mission."
            ),
        },
        "debate": {
            "beat_number": 5,
            "superhero_manifestation": (
                "The hero hesitates at the threshold of his super destiny — should he believe, accept, pursue? "
                "Can Bobby have the girl who belongs to his Nemesis? Will Scar's plan work? Should Neo believe in the unseen world? "
                "Should Maximus swear allegiance to his father's murderer? Can Peter balance Spider-Man and civilian life? "
                "In a series of refusals, the hero drags his feet before the leap."
            ),
        },
        "break_into_two": {
            "beat_number": 6,
            "superhero_manifestation": (
                "The hero commits to the 'upside-down world' of Act Two, often PROCLAIMING a new identity or accepting a mission: "
                "Bobby enters the ring against Sugar Ray with animal sounds — his drive to dominate is on; "
                "Simba flees after Mufasa's death into a world of outcasts; Neo swallows the red pill and is reborn unplugged; "
                "Maximus escapes execution, finds his family dead, and wakes as a slave doomed to die as a gladiator; "
                "Doc Ock is born when the experiment goes awry and his wife dies. "
                "The 'curse' of being special often begins here — painful, scary rebirth."
            ),
        },
        "b_story": {
            "beat_number": 7,
            "superhero_manifestation": (
                "A relationship that mirrors or tests the hero's super-ness: a super mate, a love interest, or a mentor group. "
                "Bobby woos Vickie from the smarter animals; Simba grows up among Timon and Pumbaa, the common folk; "
                "Neo and Trinity share a special bond; Maximus leads misfit gladiators under the mentor Proximo; "
                "Doc Ock's loveless descent into madness is a cautionary mirror of what Peter's unbalanced life could become. "
                "The B Story often poses: can the Superhero have love AND a mission?"
            ),
        },
        "fun_and_games": {
            "beat_number": 8,
            "superhero_manifestation": (
                "The 'promise of the premise' — we watch the hero USE his power/gift and it seems glorious: "
                "Bobby's winning streak, marriage, kids in a montage of rising dominance; "
                "Simba sings 'Hakuna Matata' in an idyllic bug-eating life — a therapeutic break from responsibility; "
                "Neo trains in martial arts and learns he can eventually dodge bullets; "
                "Maximus fights his way back from death, his gladiator skills making him a leader; "
                "Spider-Man battles Doc Ock in a bank robbery. "
                "But the curse lurks — Bobby avoids sex to stay strong, Simba avoids his duty, Neo still resists belief. "
                "The higher they fly, the harder they will hit the pavement."
            ),
        },
        "midpoint": {
            "beat_number": 9,
            "superhero_manifestation": (
                "A false victory or false defeat at the peak/trough — A and B stories cross and stakes are raised: "
                "Bobby has beaten everyone (false victory) but jealousy enters when Cathy admires his opponent; "
                "Simba's fun ends as Nala reveals Scar has destroyed the Pridelands (A+B cross); "
                "Neo visits the Oracle and is told he is NOT The One (false defeat); "
                "Maximus draws closer to Rome as Commodus unknowingly calls up the best gladiators (A+B cross); "
                "Spider-Man's powers fail, Kirsten gets engaged, Peter declares 'I am Spider-Man no more' (false defeat). "
                "The 'curse' of human weakness begins to corrode the mission."
            ),
        },
        "bad_guys_close_in": {
            "beat_number": 10,
            "superhero_manifestation": (
                "Internal team fractures and external Nemesis tightens the vise — the hero's world collapses from within and without: "
                "Bobby gives in to the mob, takes a dive, gets suspended, jealousy blooms as he suspects Cathy; "
                "Simba refuses responsibility, argues with Nala, cannot ignore the curse of duty; "
                "Cypher's betrayal is set in motion, Mouse is killed, Morpheus is captured; "
                "Maximus reveals himself as Gladiator, Commodus plots assassination; "
                "Peter tries normalcy — gives up crime fighting, catches up on homework — but crime keeps happening. "
                "The Superhero cannot outrun who he is."
            ),
        },
        "all_is_lost": {
            "beat_number": 11,
            "superhero_manifestation": (
                "The hero is stripped of his advantage — the 'whiff of death' arrives and the hero is worse off than at the start: "
                "Bobby accuses Cathy of sleeping with Joey, beats his brother, loses his only ally; "
                "Simba encounters Rafiki who shows him his dead father lives in him — 'Remember who you are'; "
                "Cypher kills the crew one by one, Morpheus is tortured, Neo faces letting his mentor die; "
                "Maximus wins but Commodus taunts him with how his family suffered in death; "
                "A fire kills someone Peter could not save despite rushing in without powers. "
                "The power is gone, the team is broken, or the hero faces the ultimate cost of his gift."
            ),
        },
        "dark_night_of_the_soul": {
            "beat_number": 12,
            "superhero_manifestation": (
                "The hero must decide who he truly is — surrender to the curse or rise to the mission: "
                "Bobby allows Sugar Ray to pummel him as penance, paying for his sins on the ropes — a crucifixion; "
                "Simba must decide whether to return and face his past; "
                "The crew must decide whether to let Morpheus die; "
                "Maximus longs to reunite with his dead family, clutching religious statues; "
                "Aunt May tells Peter 'there is a hero in all of us, even though we must give up what we want most.' "
                "Self-will alone cannot restore the power — only faith and surrender can."
            ),
        },
        "break_into_three": {
            "beat_number": 13,
            "superhero_manifestation": (
                "A and B stories cross as the hero recommits with new understanding — often a plan that gets scuttled, "
                "forcing the hero to dig deeper: "
                "Bobby slides into Florida loserdom, opens a nightclub; "
                "Simba declares 'I am going back' — supported by Nala, Timon, and Pumbaa; "
                "Neo and Trinity boldly choose to rescue Morpheus, arming themselves; "
                "Maximus plots escape and conspiracy with senators, but Commodus discovers it — forcing a new way; "
                "Peter's power returns when love combines with duty as Doc Ock hurls a car at him and Kirsten. "
                "The missing component is always faith, love, or acceptance of the curse."
            ),
        },
        "finale": {
            "beat_number": 14,
            "superhero_manifestation": (
                "The ultimate showdown with the Nemesis, always including a CRUCIFIXION beat where the hero is "
                "tortured/killed/broken and then transcends: "
                "Bobby is arrested, destroys his belt, loses everything, tries to reconcile with Joey; "
                "Simba confronts Scar, takes responsibility, Scar reveals the truth, the battle plays out; "
                "Neo rescues Morpheus, dodges bullets, is killed by Smith and resurrected by Trinity's kiss; "
                "Commodus stabs a bound Maximus then brings him to the arena — Maximus kills him with his last strength; "
                "Spider-Man stops the train with arms outstretched (crucifixion), saves Kirsten by convincing Doc Ock "
                "to re-embrace his humanity. The hero proves faith and selflessness defeat self-will and power."
            ),
        },
        "final_image": {
            "beat_number": 15,
            "superhero_manifestation": (
                "A mirror-opposite of the Opening Image showing the transformation — the price paid, the gift given: "
                "Bobby, back in the dressing room, rehearses 'I could have been a contender' — fallen from grace; "
                "Simba roars atop Pride Rock, king with Nala, the Circle of Life renewed; "
                "Neo flies into the sky, master of his powers, warning the world via phone that things have changed; "
                "Maximus reunites with his family in the afterlife — earthly duty complete; "
                "Kirsten runs from her wedding to be with Peter — by giving up everything, he has gotten both love and mission. "
                "The Superhero's journey ends in either glorious transcendence or sacrificial grace."
            ),
        },
    },
    "film_breakdowns": [
        {
            "title": "Raging Bull",
            "year": 1980,
            "sub_type": "real_life_superhero",
            "power": "Raw boxing talent and animal drive — a force of nature in the ring",
            "nemesis": "Salvy and Tommy (mob controllers of boxing), plus his own jealousy",
            "curse": (
                "Vanity, selfishness, jealousy — sexual sacrifice (avoids sex to stay strong), "
                "human weakness that corrodes his gift"
            ),
        },
        {
            "title": "The Lion King",
            "year": 1994,
            "sub_type": "storybook_superhero",
            "power": "Rightful heir to Pride Rock — born to be king, the 'chosen one'",
            "nemesis": "Scar — got the brains but not the brute strength, relies on manipulation and hyenas",
            "curse": "Guilt over father's death, fear of responsibility, running from who he is",
        },
        {
            "title": "The Matrix",
            "year": 1999,
            "sub_type": "fantasy_superhero",
            "power": "The One — can see and manipulate the Matrix, dodge bullets, transcend physics",
            "nemesis": "Agent Smith — revulsion for humanity, self-replicating program; Cypher the Judas traitor",
            "curse": (
                "Doubt and disbelief in his own identity; painful rebirth; "
                "sexual sacrifice (tempted by Woman in Red)"
            ),
        },
        {
            "title": "Gladiator",
            "year": 2000,
            "sub_type": "peoples_superhero",
            "power": "Strength, honor, and natural leadership that makes men follow him — the true chosen heir to Rome",
            "nemesis": (
                "Commodus — jealous false heir who murdered his father, "
                "headaches from 'super genius' self-will"
            ),
            "curse": (
                "Loss of family, enslavement, and the reluctance to accept the mantle; "
                "the price of refusing to be corrupted"
            ),
        },
        {
            "title": "Spider-Man 2",
            "year": 2004,
            "sub_type": "comic_book_superhero",
            "power": "Web-slinging, wall-crawling, spider-sense — classic comic book superpowers",
            "nemesis": (
                "Doc Ock — a cautionary mirror; lost love drove him to the dark side, "
                "his artificial arms urge evil"
            ),
            "curse": (
                "Cannot have love AND be a hero; powers fail when faith falters; "
                "'arachtile dysfunction' when he loses purpose"
            ),
        },
    ],
    "note_on_female_superheroes": (
        "Snyder notes an absolute dearth of female-driven Superhero stories. "
        "Attempts (Lara Croft, Elektra, Underworld, Aeon Flux, Catwoman) are pale imitations of male counterparts. "
        "Best example is Whale Rider, but it is more about prejudice than empowerment. "
        "He challenges writers to reconfigure the rules and bring more female Superheroes to screen."
    ),
    "source": "Save the Cat Goes to the Movies by Blake Snyder, Chapter 10: Superhero, pages 257-281",
}


if __name__ == "__main__":
    import json
    print(json.dumps(SUPERHERO_GENRE, indent=2))
