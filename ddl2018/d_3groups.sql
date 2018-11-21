

DELETE FROM OwnersGroups;


INSERT INTO OwnersNames(officialId, name, firstname, birthdate, 
	country, zipcode, municipality_fr, 
	municipality_nl, street_fr,
        street_nl,
        "number" ,
        boxNumber)
	SELECT DISTINCT ON (owner_officialId) owner_officialId, owner_name, 
	owner_firstname, owner_birthdate, owner_country,
	owner_zipCode, owner_municipality_fr, owner_municipality_nl, owner_street_fr,
        owner_street_nl,
        owner_number ,
        owner_boxNumber  FROM Owners_imp
	UNION
	SELECT DISTINCT ON (partner_officialId) partner_officialId, partner_name, 
	partner_firstname, partner_birthdate, partner_country,
	partner_zipCode, partner_municipality_fr, partner_municipality_nl, partner_street_fr,
        partner_street_nl,
        partner_number ,
        partner_boxNumber  FROM Owners_imp
	WHERE partner_officialId is not null;



DELETE FROM OwnersProperties;
INSERT INTO OwnersProperties ( propertySituationId,
        "order",
        partyType,
        OwnerRight,
        right_trad,
        managedBy,
        owner_UID,
        partner_UID,
        coOwner,
        anonymousOwner,
        dateSituation,
        divCad
        )
        SELECT I.propertySituationIdf, I."order", I.partyType, I.OwnerRight, I.right_trad, I.managedBy,
	  N.owner_UID AS UID1, N2.owner_UID AS UID2,I.CoOwner, I.anonymousOwner, 
	  I.dateSituation, I.divcad
	  FROM Owners_imp AS I 
	  LEFT JOIN OwnersNames AS N ON N.officialId = I.owner_officialId 
	  LEFT JOIN OwnersNames AS N2 ON N2.officialId = I.partner_officialId;

