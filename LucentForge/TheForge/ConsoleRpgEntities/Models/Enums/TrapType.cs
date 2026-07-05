namespace ConsoleRpgEntities.Models.Enums;

// W15 Phase H — [Flags] enum for composite trap types on ILockable entities.
// Teacher suggestion: "a Trap entity with multiple trigger types (Mechanical,
// Magical, Poison) is a textbook [Flags] candidate." Each bit is a distinct
// trap mechanism. A door or chest can have multiple types active at once —
// e.g., Mechanical | Poison for a spring-dart trap coated in venom.
[Flags]
public enum TrapType
{
    None       = 0,
    Mechanical = 1 << 0,   // physical dart/spike — brute-force disarm via Lockpick
    Magical    = 1 << 1,   // arcane ward — requires Intuition check (future)
    Poison     = 1 << 2,   // inflicts ongoing damage over time on trigger (future)
    Electric   = 1 << 3,   // instant paralysis on trigger (future)
}
