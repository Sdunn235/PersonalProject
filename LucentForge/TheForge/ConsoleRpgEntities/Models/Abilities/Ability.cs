using ConsoleRpgEntities.Models.Enums;

namespace ConsoleRpgEntities.Models.Abilities;

public class Ability
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public int Power { get; set; }
    public int StaminaCost { get; set; }
    public AbilityKind Kind { get; set; }
    public CoreAttribute PrimaryStat { get; set; }

    public virtual ICollection<Character> Characters { get; set; } = new List<Character>();
}
