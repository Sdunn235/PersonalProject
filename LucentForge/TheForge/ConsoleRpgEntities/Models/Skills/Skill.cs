using ConsoleRpgEntities.Models.Enums;

namespace ConsoleRpgEntities.Models.Skills;

public class Skill
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;

    public CoreAttribute PrimaryAttribute { get; set; }
    public CoreAttribute? SecondaryAttribute { get; set; }

    public virtual ICollection<CharacterSkill> CharacterSkills { get; set; } = new List<CharacterSkill>();
}
