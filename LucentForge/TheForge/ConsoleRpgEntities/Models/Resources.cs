namespace ConsoleRpgEntities.Models;

public class Resources
{
    public int Id { get; set; }

    public int Hp { get; set; }
    public int MaxHp { get; set; }

    public int Sp { get; set; }
    public int MaxSp { get; set; }

    public int BitPool { get; set; }
    public int MaxBitPool { get; set; }

    public int BytePool { get; set; }
    public int MaxBytePool { get; set; }

    public int CharacterId { get; set; }
    public virtual Character Character { get; set; } = null!;
}
