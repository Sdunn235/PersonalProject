using ConsoleRpgEntities.Models.Items;

namespace ConsoleRpgEntities.Models.Containers;

public abstract class Container : IItemContainer
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;

    public virtual ICollection<Item> ItemsCollection { get; set; } = new List<Item>();

    IEnumerable<Item> IItemContainer.Items => ItemsCollection;

    public virtual void AddItem(Item item)
    {
        item.ContainerId = Id;
        if (!ItemsCollection.Contains(item))
            ItemsCollection.Add(item);
    }

    public virtual void RemoveItem(Item item)
    {
        ItemsCollection.Remove(item);
        item.ContainerId = null;
    }
}
