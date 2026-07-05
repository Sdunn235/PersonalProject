using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using ConsoleRpgEntities.Models;
using ConsoleRpgEntities.Models.Abilities;
using ConsoleRpgEntities.Models.Containers;
using ConsoleRpgEntities.Models.Items;
using ConsoleRpgEntities.Models.Magic;
using ConsoleRpgEntities.Models.Races;
using ConsoleRpgEntities.Models.Skills;

namespace ConsoleRpgEntities.Data;

public class GameContext : DbContext, IContext
{
    // DbSets
    public DbSet<Room> Rooms { get; set; }
    public DbSet<Door> Doors { get; set; }
    public DbSet<Character> Characters { get; set; }
    public DbSet<Race> Races { get; set; }
    public DbSet<Stats> Stats { get; set; }
    public DbSet<Resources> Resources { get; set; }
    public DbSet<Ability> Abilities { get; set; }
    public DbSet<Magic> Magics { get; set; }
    public DbSet<Item> Items { get; set; }
    public DbSet<Container> Containers { get; set; }
    public DbSet<EquipmentSlot> EquipmentSlots { get; set; }
    public DbSet<Skill> Skills { get; set; }
    public DbSet<CharacterSkill> CharacterSkills { get; set; }

    // IContext explicit implementations
    IEnumerable<Room> IContext.Rooms => Rooms;
    IEnumerable<Door> IContext.Doors => Doors;
    IEnumerable<Character> IContext.Characters => Characters;
    IEnumerable<Race> IContext.Races => Races;
    IEnumerable<Stats> IContext.Stats => Stats;
    IEnumerable<Resources> IContext.Resources => Resources;
    IEnumerable<Ability> IContext.Abilities => Abilities;
    IEnumerable<Magic> IContext.Magics => Magics;
    IEnumerable<Item> IContext.Items => Items;
    IEnumerable<Container> IContext.Containers => Containers;
    IEnumerable<EquipmentSlot> IContext.EquipmentSlots => EquipmentSlots;
    IEnumerable<Skill> IContext.Skills => Skills;

    // W14 Phase D — IQueryable accessors for graded LINQ exercises that
    // call for .Include(). The DbSet<T> already implements IQueryable<T>,
    // so the implementation is a direct return.
    IQueryable<Item> IContext.QueryItems() => Items;
    IQueryable<Container> IContext.QueryContainers() => Containers;

    public void AddEntity<T>(T entity) where T : class
    {
        Set<T>().Add(entity);
    }

    public void RemoveEntity<T>(T entity) where T : class
    {
        Set<T>().Remove(entity);
    }

    void IContext.SaveChanges()
    {
        base.SaveChanges();
    }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        var configuration = new ConfigurationBuilder()
            .SetBasePath(AppContext.BaseDirectory)
            .AddJsonFile("appsettings.json", optional: false, reloadOnChange: false)
            .AddJsonFile("appsettings.Development.json", optional: true, reloadOnChange: false)
            .Build();

        var connectionString = configuration.GetConnectionString("GameDb")
            ?? throw new InvalidOperationException(
                "Connection string 'GameDb' not found. Ensure appsettings.json is present " +
                "and (for real credentials) appsettings.Development.json exists in the output directory.");

        optionsBuilder
            .UseLazyLoadingProxies()
            .UseSqlServer(connectionString);
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // --- Character TPH ---
        modelBuilder.Entity<Character>()
            .HasDiscriminator<string>("CharacterType")
            .HasValue<Player>("Player")
            .HasValue<Npc>("NPC")
            .HasValue<Animal>("Animal")
            .HasValue<Wolf>("Wolf");  // W15 Phase F3

        // --- Race TPH ---
        modelBuilder.Entity<Race>()
            .HasDiscriminator<string>("RaceType")
            .HasValue<PlayableRace>("Playable")
            .HasValue<MonsterRace>("Monster")
            .HasValue<AnimalRace>("Animal");

        // --- Item TPH ---
        // W15 Phase F1: LockedJournal added — an Item that also implements
        // ILockable. Same TryUnlock algorithm works on it with zero changes.
        modelBuilder.Entity<Item>()
            .HasDiscriminator<string>("ItemType")
            .HasValue<Weapon>("Weapon")
            .HasValue<Armor>("Armor")
            .HasValue<Shield>("Shield")
            .HasValue<Consumable>("Consumable")
            .HasValue<LockedJournal>("LockedJournal")
            .HasValue<Tome>("Tome");

        // --- Container TPH ---
        // W14 Phase C.1: Room joins Inventory/Equipment/Chest under the
        // Containers table. Items on the floor of a room are stored the same
        // way as items in any other container — same Items table, same
        // ContainerId FK, same Container.AddItem/RemoveItem semantics.
        // W15 Phase E: MonsterLoot removed. NPC loot lives in the NPC's
        // Inventory (Character already owns Inventory via Phase 1.5).
        modelBuilder.Entity<Container>()
            .HasDiscriminator<string>("ContainerType")
            .HasValue<Inventory>("Inventory")
            .HasValue<Equipment>("Equipment")
            .HasValue<Chest>("Chest")           // W13
            .HasValue<Room>("Room")             // W14 Phase C.1
            .HasValue<Bookshelf>("Bookshelf");  // W15 Phase F2

        // W13 — Chest → Room (many-to-one, nullable).
        // W14 Phase C.1: changed from SetNull to NoAction. After Room joined
        // Containers via TPH, SetNull on Chest.RoomId combined with SetNull
        // on Character.RoomId produced a SQL Server "multiple cascade paths"
        // error (Containers self-referencing through both FKs). NoAction
        // pushes cleanup responsibility to the application — RemoveRoom in
        // GameEngine already nulls Chest.RoomId / Character.RoomId and
        // removes connected Doors before the actual delete.
        modelBuilder.Entity<Chest>()
            .HasOne(c => c.Room)
            .WithMany()
            .HasForeignKey(c => c.RoomId)
            .OnDelete(DeleteBehavior.NoAction);

        // Bookshelf → Room (many-to-one, nullable). Same NoAction rationale as
        // Chest→Room: avoids SQL Server multiple-cascade-paths error.
        modelBuilder.Entity<Bookshelf>()
            .HasOne(b => b.Room)
            .WithMany()
            .HasForeignKey(b => b.RoomId)
            .OnDelete(DeleteBehavior.NoAction);

        // Container → Items (one-to-many, nullable: items can float)
        modelBuilder.Entity<Container>()
            .HasMany(c => c.ItemsCollection)
            .WithOne(i => i.Container)
            .HasForeignKey(i => i.ContainerId)
            .OnDelete(DeleteBehavior.SetNull);

        // Character ↔ Inventory (one-to-one, nullable on Character side)
        modelBuilder.Entity<Inventory>()
            .HasOne(i => i.Owner)
            .WithOne(c => c.Inventory)
            .HasForeignKey<Inventory>(i => i.OwnerCharacterId)
            .OnDelete(DeleteBehavior.ClientCascade);

        // Character ↔ Equipment (one-to-one, nullable on Character side)
        modelBuilder.Entity<Equipment>()
            .HasOne(e => e.Owner)
            .WithOne(c => c.Equipment)
            .HasForeignKey<Equipment>(e => e.OwnerCharacterId)
            .OnDelete(DeleteBehavior.ClientCascade);

        // Equipment → EquipmentSlots (one-to-many; EquipmentContainerId nullable on slot)
        modelBuilder.Entity<Equipment>()
            .HasMany(e => e.Slots)
            .WithOne(s => s.EquipmentContainer)
            .HasForeignKey(s => s.EquipmentContainerId)
            .OnDelete(DeleteBehavior.Cascade);

        // --- Character relationships ---

        // Character → Stats (one-to-one)
        modelBuilder.Entity<Character>()
            .HasOne(c => c.Stats)
            .WithOne(s => s.Character)
            .HasForeignKey<Stats>(s => s.CharacterId);

        // Character → Resources (one-to-one)
        modelBuilder.Entity<Character>()
            .HasOne(c => c.Resources)
            .WithOne(r => r.Character)
            .HasForeignKey<Resources>(r => r.CharacterId);

        // Character → Race (many-to-one, nullable)
        modelBuilder.Entity<Character>()
            .HasOne(c => c.Race)
            .WithMany(r => r.Characters)
            .HasForeignKey(c => c.RaceId)
            .OnDelete(DeleteBehavior.SetNull);

        // Character → Room (many-to-one, nullable).
        // W14 Phase C.1: NoAction (was SetNull) — see Chest→Room comment above.
        modelBuilder.Entity<Character>()
            .HasOne(c => c.Room)
            .WithMany(r => r.Characters)
            .HasForeignKey(c => c.RoomId)
            .OnDelete(DeleteBehavior.NoAction);

        // Character ↔ Ability (many-to-many via CharacterAbilities)
        modelBuilder.Entity<Character>()
            .HasMany(c => c.Abilities)
            .WithMany(a => a.Characters)
            .UsingEntity(j => j.ToTable("CharacterAbilities"));

        // Character ↔ Magic (many-to-many via CharacterMagic)
        modelBuilder.Entity<Character>()
            .HasMany(c => c.Magics)
            .WithMany(m => m.Characters)
            .UsingEntity(j => j.ToTable("CharacterMagic"));

        // --- CharacterSkill (explicit join with Proficiency) ---
        modelBuilder.Entity<CharacterSkill>()
            .HasKey(cs => new { cs.CharacterId, cs.SkillId });

        modelBuilder.Entity<CharacterSkill>()
            .HasOne(cs => cs.Character)
            .WithMany(c => c.CharacterSkills)
            .HasForeignKey(cs => cs.CharacterId);

        modelBuilder.Entity<CharacterSkill>()
            .HasOne(cs => cs.Skill)
            .WithMany(s => s.CharacterSkills)
            .HasForeignKey(cs => cs.SkillId);

        // --- EquipmentSlot → Item (many-to-one, nullable for empty slots) ---
        modelBuilder.Entity<EquipmentSlot>()
            .HasOne(es => es.EquippedItem)
            .WithMany()
            .HasForeignKey(es => es.EquippedItemId)
            .OnDelete(DeleteBehavior.SetNull);

        // --- Door ↔ Room (bidirectional; one Door row per passage) ---
        // W14 Phase C.2: Door is bidirectional. Two FKs to Room (RoomA/RoomB)
        // each map to a Room.DoorsAsA / DoorsAsB collection. Restrict on
        // delete — RemoveRoom handles cleanup application-side.
        modelBuilder.Entity<Door>()
            .HasOne(d => d.RoomA)
            .WithMany(r => r.DoorsAsA)
            .HasForeignKey(d => d.RoomAId)
            .OnDelete(DeleteBehavior.Restrict);

        modelBuilder.Entity<Door>()
            .HasOne(d => d.RoomB)
            .WithMany(r => r.DoorsAsB)
            .HasForeignKey(d => d.RoomBId)
            .OnDelete(DeleteBehavior.Restrict);

        base.OnModelCreating(modelBuilder);
    }
}
