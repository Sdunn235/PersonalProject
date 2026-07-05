using ConsoleRpgEntities.Models.Enums;

namespace ConsoleRpgEntities.Models.Magic;

public class Magic
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public int Power { get; set; }
    public int BitPoolCost { get; set; }
    public int BytePoolCost { get; set; }
    public Element Element { get; set; }
    public MagicKind Kind { get; set; }
    public CoreAttribute PrimaryStat { get; set; }

    public virtual ICollection<Character> Characters { get; set; } = new List<Character>();
}
