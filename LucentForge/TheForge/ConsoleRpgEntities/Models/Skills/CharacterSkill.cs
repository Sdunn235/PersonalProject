namespace ConsoleRpgEntities.Models.Skills;

public class CharacterSkill
{
    public int CharacterId { get; set; }
    public virtual Character Character { get; set; } = null!;

    public int SkillId { get; set; }
    public virtual Skill Skill { get; set; } = null!;

    public int Proficiency { get; set; }
}
