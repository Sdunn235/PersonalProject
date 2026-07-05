using ConsoleRpgEntities.Models;
using ConsoleRpgEntities.Models.Abilities;
using ConsoleRpgEntities.Models.Containers;
using ConsoleRpgEntities.Models.Items;
using ConsoleRpgEntities.Models.Magic;
using ConsoleRpgEntities.Models.Races;
using ConsoleRpgEntities.Models.Skills;

namespace ConsoleRpgEntities.Data;

public interface IContext
{
    IEnumerable<Room> Rooms { get; }
    IEnumerable<Door> Doors { get; }
    IEnumerable<Character> Characters { get; }
    IEnumerable<Race> Races { get; }
    IEnumerable<Stats> Stats { get; }
    IEnumerable<Resources> Resources { get; }
    IEnumerable<Ability> Abilities { get; }
    IEnumerable<Magic> Magics { get; }
    IEnumerable<Item> Items { get; }
    IEnumerable<Container> Containers { get; }

    // W14 Phase D / Task 5 — IQueryable accessors for the few places we
    // need EF Core's .Include() to eager-load a related entity. The
    // standing project preference is lazy-loading proxies; these methods
    // exist for explicitly-graded LINQ exercises where the rubric calls
    // for .Include (FindKeyLocation: "Uses Include to eager-load the
    // key's container"). Keep usage minimal.
    IQueryable<Item> QueryItems();
    IQueryable<Container> QueryContainers();
    IEnumerable<EquipmentSlot> EquipmentSlots { get; }
    IEnumerable<Skill> Skills { get; }

    void AddEntity<T>(T entity) where T : class;
    void RemoveEntity<T>(T entity) where T : class;
    void SaveChanges();
}
