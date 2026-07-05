# CONTRIBUTIONS

> Required for all tiers. This file is an honest project history from the beginning of the semester through the final TheForge state. It separates what came from the class template, what came from my own work, and where AI collaboration helped me reason through design, migrations, bugs, and documentation.

---

## 1. Starting Point

This repository began as the GitHub Classroom starter repo for the WCTC .NET Database Programming course. The first real work was not TheForge yet; it started as a smaller file I/O and character-management project where I was learning how to structure a C# console application, read and write data, separate classes into their own files, and use Git/GitHub more seriously across my PC and laptop.

The earliest commits show that progression: initial project setup, CSVHelper refactoring, moving `Character` into its own file, then reorganizing the code around SRP and LINQ queries. From there the project became a running semester-long architecture exercise. Each week added a new principle or database concept instead of starting over from scratch.

By the time the project reached W15, the starting point was not a blank template. It already contained my W9-W14 work: EF Core setup, SQL Server configuration, TPH inheritance, abilities, equipment, inventories, containers, chests, lockable objects, rooms, doors, secret-door inspection, LINQ queries, and the early seeded dungeon world. W15 was built by carrying that existing codebase forward, not by replacing it with the W15 template implementation.

The W15 template README and `CONTRIBUTIONS.md` template were used as scaffolding for documentation and grading expectations. I did not copy the W15 template implementation files such as `MapManager.cs`, `ExplorationUI.cs`, `PlayerService.cs`, `AdminService.cs`, or `ParserDemo.cs`. My implementation kept the existing two-project structure and continued building mostly through `ConsoleRpg`, `ConsoleRpgEntities`, the model layer, migrations, and `GameEngine.cs`.

---

## 2. What I Added

### Early File I/O and SOLID Foundation

In the first part of the semester, I built the base character-management project and gradually refactored it into cleaner pieces. This included CSV handling, separating the `Character` class, organizing services, and adding LINQ queries. The major design lesson here was learning that code should not all live in `Program.cs`. The project started moving toward services and responsibilities instead of one large script.

I then added OCP work by introducing an `IFileHandler` abstraction with CSV and JSON implementations. That was one of the first times the project showed a real design principle instead of just assignment features. The application could switch file formats through an abstraction instead of hardcoding one storage format everywhere.

For LSP/ISP and DIP work, I restructured the hierarchy, added races/classes/behavior interfaces, and built a two-project SOLID architecture. This is where the project began forming the habit that later became important in TheForge: build behavior around contracts and let concrete classes plug into those contracts.

### W9-W10: EF Core, SQL Server, and Inheritance

The project shifted from file-based persistence into EF Core and SQL Server. I added database CRUD, evolved `IContext`, configured lazy loading proxies, and connected to the school SQL Server. This was the foundation for treating the project as a real database-backed application instead of a console-only exercise.

In W10, I added EF Core TPH inheritance for `Character` and `Ability` types, many-to-many relationships, migrations, and the first serious version of the entity model. That was the point where the project started becoming a world model instead of just a character list.

### W11-W12: Equipment, Inventory, Containers, Items

W11 added equipment and room navigation ideas. The code began moving closer to a game architecture, with characters carrying gear and the world having places to move through.

W12 added the major `Item` and `Container` hierarchy. This became one of the most important foundations in the whole project. Items could be weapons, armor, consumables, or key items. Containers could represent inventory, equipment, chests, monster loot, and eventually rooms and bookshelves. This was also where LINQ operations and seed migrations became more meaningful because the data model had enough shape to ask real questions about the world.

### W13: Chests, MonsterLoot, Lockpicks, and Character Capability

W13 added chests, monster loot, lockpicks, and more complete character/container behavior. At this stage, `MonsterLoot` still existed as a separate container type. It worked for a game assignment, but it later became the architectural piece I removed because it treated enemies like loot dispensers instead of entities.

W13 also included cleanup, character CRUD improvements, a shield, menu reshaping, BitPool naming, derived resource display, and what I think of as the “universal character capability promotion.” That promotion mattered because characters became more complete entities with inventory and equipment. It later made the `MonsterLoot` removal possible.

### W14: Rooms, Doors, Secret Doors, and LSP Refactor

W14 moved the world forward by making `Room` a `Container` subclass and adding bidirectional `Door` records. Doors implemented `ILockable`, which meant the same lock/unlock concept could apply beyond chests.

The biggest W14 design payoff was the `TryUnlock` LSP refactor and secret-door inspection. Instead of writing separate unlock logic for every object type, the project began using `ILockable` as a behavioral contract. That decision carried directly into W15 when `LockedJournal` became another lockable object without needing a new unlock algorithm.

W14 also added better item placement, key handling through a `KeyId` sentinel instead of a separate `IsKeyItem` flag, better loot picker UX, encumbrance fixes, and graded LINQ/Spectre.Console polish.

### W15 Submission: TheForge and the Simulation-First Turn

W15 is where the project became TheForge. The most important architectural decision was eliminating `MonsterLoot`. Instead of giving defeated enemies a separate loot bucket, enemy loot now lives in the NPC's actual inventory. That matters because an NPC should be an entity with possessions, not a reward dispenser created for the player.

I added `LockedJournal : Item, ILockable`, proving the existing unlock system worked on a third kind of object without rewriting the algorithm. I also added `Bookshelf : Container` and `Tome : Item` so the world could hold readable lore. Gobby's journal and the tribe's tome tell conflicting versions of the same story, which was intentional: I wanted the database to support perspective, not just objective exposition.

I added `Wolf : Npc` with `PackSize` to prove the inventory change was not only about Gobby. I also added W15 LINQ queries: `InventoryAudit`, `MostDangerousRoom`, and `LockedTreasures`. The strongest one is `LockedTreasures`, because it pulls together chests, doors, and journals through shared lockable behavior.

I also added character selection and clearer menu sections so the project was easier to demonstrate live.

I kept extending TheForge toward a playable dungeon demo and a stronger LucentForge foundation. This included the Play/Admin mode split, title screen, bug fixes, `[Flags]` enums for `TrapType` and `SlotType`, a room-first player loop, Spectre.Console combat, floor item pickup, room grid coordinates, an ASCII mini-map, lockpick semantics, a map redesign, tome reading from inventory, combat menu improvements, ability/magic seeds, BitPool/BytePool fixes, a 7-room dungeon redesign, NPC dialogue, Mira shop fixes, playtest bug fixes, persistent messages across player loop ticks, and `AdminResetWorld` for resetting the world safely.

The post-grade polish matters because it shows where this project is going: away from a menu-only database assignment and toward a playable simulation-driven RPG prototype.

---

## 3. What I Used From the Template / AI / Other Sources

The original repository came from the GitHub Classroom starter/template. The course templates provided the assignment structure, rubrics, and some conceptual expectations for each week. For W15 specifically, I used the README and `CONTRIBUTIONS.md` template as documentation scaffolding, but I did not copy the W15 implementation files.

I used AI heavily throughout the semester, especially Claude, as a programming and architecture collaborator. AI helped with code review, planning, migration guidance, debugging, naming, documentation, and reasoning through bigger design choices. I also used AI to help keep the project organized when the model became large enough that holding everything in my head at once was difficult.

That said, I am not claiming I typed every character by hand. I am claiming that I understand what the project does, why the major architecture decisions exist, and how to walk through the important pieces of code. I can explain the purpose of the entity hierarchy, the container hierarchy, the `ILockable` interface, the migration that removed `MonsterLoot`, and why those decisions matter for a simulation-driven RPG world.

The most important design instincts were mine: wanting the project to become more than a disposable class assignment, wanting NPCs to feel like real entities, wanting Gobby's story to have conflicting records, and wanting the database to become the spine of LucentForge.

---

## 4. Reflection on This Project

This project became much bigger than I expected. It started as course work, but it became the first real database spine for LucentForge. The biggest thing I learned is that architecture choices are not just technical. They change what kind of world the software can become.

The `MonsterLoot` decision is the best example. It would have been easy to leave it alone because it worked well enough for a normal RPG assignment. But the more I looked at it, the more wrong it felt. If enemies already have inventories, then their items should belong to them. When they are defeated, the world state changes, but the items should not magically come from a separate loot bucket. Removing `MonsterLoot` made the schema simpler, but more importantly, it made it more honest.

The `ILockable` work also stuck with me. At first, interfaces felt like something I was supposed to use because the class said so. By the end, I could actually see why they mattered. A chest, a door, and a locked journal are not the same kind of object, but they can share the same lockable behavior. That is the Liskov Substitution Principle becoming visible in a real feature instead of just a definition.

I also learned how hard migrations can be when the schema is no longer trivial. EF Core can scaffold changes, but it does not automatically understand the meaning of the data. The migration that removed `MonsterLoot` had to preserve ownership correctly before dropping the old structure. That taught me to treat migrations as part of the architecture, not just generated files.

The hardest part of the project was the scale. `GameEngine.cs` grew large, and I cannot pretend I can recite every line from memory. But I can explain the important systems, how they connect, and why they were built that way. I can walk through the entity model, the core interactions, the queries, the migrations, and the live demo path.

What I am most proud of is that TheForge started to feel like a world. NPCs have inventory. Rooms contain objects. Doors connect spaces. Books can disagree with journals. Queries can ask meaningful questions. The database is not just storing data anymore; it is starting to describe a living place.

---

## 5. Course Feedback (NOT graded — Shawn fills this in)

**What did you learn that genuinely stuck with you?**
This class will forever be invaluable to me for the way it changed how I think about software. The SOLID principles are not just abstract rules, they are design tools that shape the kind of software you can build. The way architecture choices affect the world model is something I will carry forward in all my projects.

**What did you like about the course?**
When I learned this was going to be a RPG database I was locked in. I knew instantly that it would progress me furthur toward my dream of making games. The way the project built week by week, with each principle adding a new layer, was really effective for learning. I also appreciated the flexibility to build something that felt like a real world instead of just a contrived assignment. Truthfully watching decision making, errors arise, and solving them was one of the best things. I struggle with how to start and where to start and so watching a teacher work through that was meaningful. Even if it wasn't planned.

**What didn't work for you?**
Writing the code. I understand the concepts and can read through the code, but I have a hard time writing it myself. I understand the architecture and can explain it, but I cannot type out the whole thing from scratch. With dyslexia, ADHD, and other mental disabilities. I make to many small mistakes and executive dysfunction is hard to start things. This is the biggest reason why I have been so reliant on AI. I can explain the code, but I cannot write it without a lot of help. I wish there was a way to demonstrate my understanding without having to write every line by hand. 

**What surprised you?**
Back in my microsoft database class, I thought I wouldn't need it that much. I didn't understand the use of databases in game development. I thought I would just use files. But now I see how powerful a database can be for managing complex world state, relationships, and queries. It surprised me how much the database became the backbone of the game world instead of just a storage layer. Something I thought I would end up hating I am actually enjoying and starting to love.

**What was the hardest part of the semester (not just this project)?**
Making sure I understood the architecture and could explain it, even when I couldn't write it from scratch. I would dive in deep to learn what was going on in the code and structure. So time management was hard because I wanted to understand every detail, but that took a lot of time. I also struggled with the scale of the project. As it grew, it became harder to keep everything in my head at once. I had to learn to trust the architecture and be able to navigate the code without memorizing every line.

**What would you ADD to next year's version?**
I am not sure but some of the things that was done in class that I found helpful was when the instructor would do ULM or flow chart diagrams. Those tid bit visuals really helped me understand the architecture and flow of the code. But starting from scratch and making part of a workflow I am failing how to successfully achieve.

**What would you REMOVE or shorten?**
Nothing. I wish there was more time to go into more depth on certain topics, but I understand the constraints.

**Anything else?**
Thank you for a great semester. I learned a lot and I am excited to carry these lessons forward into my game development journey. TheForge is just the beginning of what I hope to build with this knowledge. The next big changes in my game development will be driven by the architecture I learned in this class, and I am grateful for that foundation. You have definitely shaped how I think Mark, for the better and will influence my work for years to come. Thank you for everything.

---

## Commit Review Summary

This is the high-level commit history I used to verify the project arc:

- **C0001-C0005:** setup, CSVHelper/file I/O cleanup, `Character` separation, SRP, services, LINQ.
- **C0006-C0010:** OCP file handler abstraction, LSP/ISP restructuring, DIP, two-project SOLID architecture.
- **C0011-C0012:** W9 EF Core CRUD, `IContext`, lazy loading, school SQL Server.
- **C0013-C0014:** W10 EF Core TPH setup, Character/Ability inheritance, many-to-many, migrations.
- **C0015-C0016:** W11/W12 equipment, room navigation ideas, inventory/container/item hierarchy, seed migration, LINQ polish.
- **C0017-C0020:** W13 chests, MonsterLoot, lockpicks, menu cleanup, derived resources, universal character capability promotion.
- **C0021-C0034:** W14 setup, Room as Container, Door + ILockable, item placement, key sentinel, secret doors, LSP unlock refactor, graded LINQ and Spectre.Console intro.
- **C0035-C0042:** W15 graded TheForge submission: kill MonsterLoot, add LockedJournal, Bookshelf/Tome, Wolf, LINQ queries, UX polish, documentation.
- **C0043-C0055:** post-grade playable demo polish: Play/Admin split, `[Flags]` enums, player loop, combat, mini-map, 7-room redesign, dialogue, bug fixes, pause/clear behavior, AdminResetWorld, docs rewrite.
