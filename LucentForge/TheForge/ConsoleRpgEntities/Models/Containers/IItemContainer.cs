using ConsoleRpgEntities.Models.Items;

namespace ConsoleRpgEntities.Models.Containers;

public interface IItemContainer
{
    int Id { get; }
    string Name { get; set; }
    IEnumerable<Item> Items { get; }
    void AddItem(Item item);
    void RemoveItem(Item item);
}
