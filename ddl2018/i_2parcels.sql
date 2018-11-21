
INSERT INTO ParcelsStreets ( nisCom, street_situation, street_translation, street_code)
	SELECT DISTINCT ON (niscom, street_code) niscom, street_situation, street_translation, street_code
	FROM Parcels_imp;

INSERT INTO Parcels ( 
	propertySituationId, MuKey,
        divCad, section, primaryNumber,
        bisNumber, exponentLetter, exponentNumber,
        partNumber, capakey, nature,
        descriptPrivate, block, floor, floorSituation,
        crossDetail, matUtil, notTaxedMatUtil, nisCom,
        street_UID, number, dateSituation, Group_UID)
	SELECT DISTINCT ON (I.propertySituationIdf, I.capakey, I.niscom, 
		I.descriptPrivate, I.block,
		I.floor, I.floorSituation, I.crossDetail,
	                    I.matUtil, I.notTaxedMatUtil)
	I.propertySituationIdf, 0,
        I.divCad, I.section, I.primaryNumber,
        I.bisNumber, I.exponentLetter, I.exponentNumber,
        I.partNumber, I.capakey, I.nature,
        I.descriptPrivate, I.block, I.floor, I.floorSituation,
        I.crossDetail, I.matUtil, I.notTaxedMatUtil, I.nisCom,
        P.street_UID, I.number, I.dateSituation, 0
	FROM Parcels_Imp AS I
	LEFT JOIN ParcelsStreets AS P ON (P.niscom = I.niscom AND 
		P.street_code = I.street_code);

INSERT INTO Parcels_CC (
        propertySituationId, constructionIndication,
        constructionType, constructionYear,
        floorNumberAboveground, garret,
        physModYear, constructionQuality,
        garageNumber, centralHeating,
        bathroomNumber, housingUnitNumber,
        placeNumber, builtSurface,
        usedSurface, CC)
	SELECT 
        I.propertySituationIdf, I.constructionIndication,
        I.constructionType, I.constructionYear,
        I.floorNumberAboveground, I.garret,
        I.physModYear, I.constructionQuality,
        I.garageNumber, I.centralHeating,
        I.bathroomNumber, I.housingUnitNumber,
        I.placeNumber, I.builtSurface,
        I.usedSurface, 0 
	FROM Parcels_Imp AS I;
	
INSERT INTO Parcels_RC ( propertySituationId, "order", polWa,
        surfaceNotTaxable, surfaceTaxable, surfaceVerif,
        soilIndex, soilRent, cadastralIncomePerSurface,
        cadastralIncomePerSurfaceOtherDi,
        numberCadastralIncome, charCadastralIncome,
        cadastralIncome, dateEndExoneration, decrete,
        dateSituation)
	SELECT propertySituationIdf, "order", polWa,
        surfaceNotTaxable, surfaceTaxable, surfaceVerif,
        soilIndex, soilRent, cadastralIncomePerSurface,
        cadastralIncomePerSurfaceOtherDi,
        numberCadastralIncome, charCadastralIncome,
        cadastralIncome, dateEndExoneration, decrete,
        dateSituation 
	FROM Parcels_Imp ;



