using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    public partial class W15_FixOutcastTome : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // The tribe's record acknowledges Gobby chose another name but dismisses it —
            // names don't change what he is to them. Sharpens the contradiction with his journal.
            migrationBuilder.Sql(@"
                UPDATE Items
                SET LoreText = N'Let the record show:

Grubnak of the Sharp Eye was a scout of the Blackthorn Swarm.
On the night of the third raid, he abandoned his post.
Three clutchmates were taken because the flank was unwatched.

He calls himself free. We have heard he has taken another name for himself.
Names do not change what a creature is.
He will always be Grubnak to us.

He stole from the Warchief''s table and fled into the dungeon dark.
If found, he is to be returned. Alive is preferred. Not required.

This account is sealed by the Warchief''s mark.'
                WHERE Name = N'On the Outcast' AND ItemType = 'Tome';
            ");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(@"
                UPDATE Items
                SET LoreText = N'Let the record show:

Grubnak of the Sharp Eye was a scout of the Blackthorn Swarm.
On the night of the third raid, he abandoned his post.
Three clutchmates were taken because the flank was unwatched.

He calls himself free. We call him a deserter.
He stole from the Warchief''s table and fled into the dungeon dark.
If found, he is to be returned. Alive is preferred. Not required.

This account is sealed by the Warchief''s mark.'
                WHERE Name = N'On the Outcast' AND ItemType = 'Tome';
            ");
        }
    }
}
