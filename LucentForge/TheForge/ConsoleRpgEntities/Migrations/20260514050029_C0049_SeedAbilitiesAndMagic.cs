using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    public partial class C0049_SeedAbilitiesAndMagic : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // Seed Abilities, Magic, and link them to Elara.
            // Enum values used below:
            //   AbilityKind: Attack=0, Heal=1, Defend=2, Utility=3
            //   MagicKind:   Attack=0, Heal=1, Buff=2, Debuff=3, Utility=4
            //   CoreAttribute: Physique=0, Reflexes=1, Constitution=2, Intellect=3, Intuition=4, Linguistic=5, Luck=6
            //   Element: Neutral=0, Fire=1, Water=2, Earth=3, Air=4, Light=5, Void=6
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;
                DECLARE @ElaraId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Elara the Bold' AND CharacterType = 'Player');

                -- ── Abilities ──────────────────────────────────────────────────
                -- Power Strike: heavy physical hit (AbilityKind=Attack=0, PrimaryStat=Physique=0)
                IF NOT EXISTS (SELECT 1 FROM Abilities WHERE Name = N'Power Strike')
                    INSERT INTO Abilities (Name, Description, Power, StaminaCost, Kind, PrimaryStat)
                    VALUES (N'Power Strike', N'A focused blow that drives past the enemy''s guard.', 12, 8, 0, 0);

                -- Shield Bash: interrupt + small damage (AbilityKind=Defend=2, PrimaryStat=Constitution=2)
                IF NOT EXISTS (SELECT 1 FROM Abilities WHERE Name = N'Shield Bash')
                    INSERT INTO Abilities (Name, Description, Power, StaminaCost, Kind, PrimaryStat)
                    VALUES (N'Shield Bash', N'Slam your shield into the enemy, staggering them.', 6, 5, 2, 2);

                -- Second Wind: self-heal (AbilityKind=Heal=1, PrimaryStat=Constitution=2)
                IF NOT EXISTS (SELECT 1 FROM Abilities WHERE Name = N'Second Wind')
                    INSERT INTO Abilities (Name, Description, Power, StaminaCost, Kind, PrimaryStat)
                    VALUES (N'Second Wind', N'Draw on reserves — recover stamina mid-fight.', 0, 0, 1, 2);

                DECLARE @PowerStrikeId INT = (SELECT TOP 1 Id FROM Abilities WHERE Name = N'Power Strike');
                DECLARE @ShieldBashId  INT = (SELECT TOP 1 Id FROM Abilities WHERE Name = N'Shield Bash');
                DECLARE @SecondWindId  INT = (SELECT TOP 1 Id FROM Abilities WHERE Name = N'Second Wind');

                -- Link Elara to all three abilities
                IF @ElaraId IS NOT NULL AND @PowerStrikeId IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM CharacterAbilities WHERE AbilitiesId = @PowerStrikeId AND CharactersId = @ElaraId)
                    INSERT INTO CharacterAbilities (AbilitiesId, CharactersId) VALUES (@PowerStrikeId, @ElaraId);

                IF @ElaraId IS NOT NULL AND @ShieldBashId IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM CharacterAbilities WHERE AbilitiesId = @ShieldBashId AND CharactersId = @ElaraId)
                    INSERT INTO CharacterAbilities (AbilitiesId, CharactersId) VALUES (@ShieldBashId, @ElaraId);

                IF @ElaraId IS NOT NULL AND @SecondWindId IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM CharacterAbilities WHERE AbilitiesId = @SecondWindId AND CharactersId = @ElaraId)
                    INSERT INTO CharacterAbilities (AbilitiesId, CharactersId) VALUES (@SecondWindId, @ElaraId);

                -- ── Magic ───────────────────────────────────────────────────────
                -- Bit Flash: fast low-cost electric arc (MagicKind=Attack=0, Element=Neutral=0, PrimaryStat=Intuition=4)
                IF NOT EXISTS (SELECT 1 FROM Magics WHERE Name = N'Bit Flash')
                    INSERT INTO Magics (Name, Description, Power, BitPoolCost, BytePoolCost, Element, Kind, PrimaryStat)
                    VALUES (N'Bit Flash', N'A crackling discharge of raw Bit energy — cheap and quick.', 8, 6, 0, 0, 0, 4);

                -- Byte Bolt: heavier structured spell (MagicKind=Attack=0, Element=Void=6, PrimaryStat=Intellect=3)
                IF NOT EXISTS (SELECT 1 FROM Magics WHERE Name = N'Byte Bolt')
                    INSERT INTO Magics (Name, Description, Power, BitPoolCost, BytePoolCost, Element, Kind, PrimaryStat)
                    VALUES (N'Byte Bolt', N'A compressed burst of Byte-code that shreds through defences.', 15, 0, 8, 6, 0, 3);

                -- Data Mend: healing spell (MagicKind=Heal=1, Element=Light=5, PrimaryStat=Intuition=4)
                IF NOT EXISTS (SELECT 1 FROM Magics WHERE Name = N'Data Mend')
                    INSERT INTO Magics (Name, Description, Power, BitPoolCost, BytePoolCost, Element, Kind, PrimaryStat)
                    VALUES (N'Data Mend', N'Rewrite the body''s error-state — restore HP between encounters.', 20, 4, 0, 5, 1, 4);

                DECLARE @BitFlashId  INT = (SELECT TOP 1 Id FROM Magics WHERE Name = N'Bit Flash');
                DECLARE @ByteBoltId  INT = (SELECT TOP 1 Id FROM Magics WHERE Name = N'Byte Bolt');
                DECLARE @DataMendId  INT = (SELECT TOP 1 Id FROM Magics WHERE Name = N'Data Mend');

                -- Link Elara to all three spells
                IF @ElaraId IS NOT NULL AND @BitFlashId IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM CharacterMagic WHERE MagicsId = @BitFlashId AND CharactersId = @ElaraId)
                    INSERT INTO CharacterMagic (MagicsId, CharactersId) VALUES (@BitFlashId, @ElaraId);

                IF @ElaraId IS NOT NULL AND @ByteBoltId IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM CharacterMagic WHERE MagicsId = @ByteBoltId AND CharactersId = @ElaraId)
                    INSERT INTO CharacterMagic (MagicsId, CharactersId) VALUES (@ByteBoltId, @ElaraId);

                IF @ElaraId IS NOT NULL AND @DataMendId IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM CharacterMagic WHERE MagicsId = @DataMendId AND CharactersId = @ElaraId)
                    INSERT INTO CharacterMagic (MagicsId, CharactersId) VALUES (@DataMendId, @ElaraId);
            ");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;
                DECLARE @ElaraId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Elara the Bold' AND CharacterType = 'Player');

                -- Remove Elara's ability and magic links
                IF @ElaraId IS NOT NULL
                BEGIN
                    DELETE FROM CharacterAbilities WHERE CharactersId = @ElaraId;
                    DELETE FROM CharacterMagic WHERE CharactersId = @ElaraId;
                END

                -- Remove the seeded abilities and magic
                DELETE FROM Abilities WHERE Name IN (N'Power Strike', N'Shield Bash', N'Second Wind');
                DELETE FROM Magics WHERE Name IN (N'Bit Flash', N'Byte Bolt', N'Data Mend');
            ");
        }
    }
}
