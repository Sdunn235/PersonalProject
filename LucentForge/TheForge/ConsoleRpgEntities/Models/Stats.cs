namespace ConsoleRpgEntities.Models;

public class Stats
{
    public int Id { get; set; }

    public int Physique { get; set; }
    public int Reflexes { get; set; }
    public int Constitution { get; set; }
    public int Intellect { get; set; }
    public int Intuition { get; set; }
    public int Linguistic { get; set; }
    public int Luck { get; set; }

    public int CharacterId { get; set; }
    public virtual Character Character { get; set; } = null!;
}
