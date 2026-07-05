namespace ConsoleRpgEntities.Models.Races;

public abstract class Race
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;

    public virtual ICollection<Character> Characters { get; set; } = new List<Character>();
}
