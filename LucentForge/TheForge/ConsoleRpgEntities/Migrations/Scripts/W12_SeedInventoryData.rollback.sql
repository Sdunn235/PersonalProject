-- W12_SeedInventoryData.rollback.sql
-- Removes Elara's seeded rows in reverse FK order.
-- Races seeded by W12 remain — other test data may reference them.

SET NOCOUNT ON;

DECLARE @ElaraId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Elara the Bold' AND CharacterType = 'Player');

IF @ElaraId IS NOT NULL
BEGIN
    DECLARE @InvId INT   = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Inventory' AND Inventory_OwnerCharacterId = @ElaraId);
    DECLARE @EquipId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Equipment' AND OwnerCharacterId = @ElaraId);

    -- Slots and items first (containers' FKs reference them)
    DELETE FROM EquipmentSlots WHERE CharacterId = @ElaraId;

    DELETE FROM Items WHERE ContainerId IN (@InvId, @EquipId);

    DELETE FROM Containers WHERE Id IN (@InvId, @EquipId);

    DELETE FROM Resources WHERE CharacterId = @ElaraId;
    DELETE FROM Stats     WHERE CharacterId = @ElaraId;
    DELETE FROM Characters WHERE Id = @ElaraId;
END;
