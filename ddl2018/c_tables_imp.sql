
/*
DROP TABLE IF EXISTS OwnersGroups;
CREATE TABLE OwnersGroups
 (
	Group_UID			bigint NOT NULL, 
	owner_UID			bigint NOT NULL, 
	dateSituation			date
);


DROP TABLE IF EXISTS Groups;
CREATE TABLE Groups
(
	Group_UID			bigint
);
*/

DROP TABLE IF EXISTS Global_Natures;
CREATE TABLE Global_Natures
 (
	Nature_PK			Integer, 
	Nature_FR			Character varying (44), 
	Nature_GE			Character varying (44), 
	Nature_NL			Character varying (44), 
	Obsolete			Boolean NOT NULL
);

DROP TABLE IF EXISTS OwnersNames;
CREATE TABLE OwnersNames
 (
	Owner_UID			serial, 
	officialId			Character varying (30), 
	name				Character varying (400), 
	firstname			Character varying (180), 
	birthdate			date, 
	country				Character varying (4), 
	zipCode				Character varying (30), 
	municipality_fr			Character varying (100), 
	municipality_nl			Character varying (100), 
	street_fr			Character varying (300), 
	street_nl			Character varying (300), 
	number				Character varying (20), 
	boxNumber			Character varying (20)
);

DROP TABLE IF EXISTS OwnersProperties;
CREATE TABLE OwnersProperties
 (
	Situation_UID			serial, 
	Group_UID			bigint, 
	propertySituationId		bigint NOT NULL, 
	"order"				Integer, 
	partyType			Integer, 
	OwnerRight			Character varying (120), 
	right_trad			Character varying (102), 
	managedBy			Character varying (4), 
	owner_UID			bigint, 
	partner_UID			bigint, 
	coOwner				Character varying (120), 
	anonymousOwner			Character varying (120), 
	dateSituation			date, 
	divCad				bigint
);

DROP TABLE IF EXISTS Parcels;
CREATE TABLE Parcels
 (
	propertySituationId		bigint NOT NULL, 
	MuKey				bigint, 
	divCad				bigint, 
	section				Character varying (2), 
	primaryNumber			Integer, 
	bisNumber			Character varying (6), 
	exponentLetter			Character varying (2), 
	exponentNumber			Character varying (6), 
	partNumber			Character varying (10), 
	capakey				Character varying (34), 
	nature				Integer, 
	descriptPrivate			Character varying (100), 
	block				Character varying (20), 
	floor				Character varying (20), 
	floorSituation			Character varying (60), 
	crossDetail			Character varying (60), 
	matUtil				Character varying (60), 
	notTaxedMatUtil			Character varying (10), 
	nisCom				bigint, 
	street_UID			bigint, 
	number				Character varying (20), 
	dateSituation			date, 
	Group_UID			bigint
);

DROP TABLE IF EXISTS Parcels_CC;
CREATE TABLE Parcels_CC
 (
	Parcels_CC_PK			serial, 
	propertySituationId			bigint NOT NULL, 
	constructionIndication			Integer, 
	constructionType			Character varying (40), 
	constructionYear			Character varying (8), 
	floorNumberAboveground			Character varying (510), 
	garret			Character varying (2), 
	physModYear			Character varying (8), 
	constructionQuality			Character varying (2), 
	garageNumber			Integer, 
	centralHeating			Character varying (2), 
	bathroomNumber			Integer, 
	housingUnitNumber			Integer, 
	placeNumber			Integer, 
	builtSurface			bigint, 
	usedSurface			bigint, 
	CC			Character varying (110)
);

DROP TABLE IF EXISTS Parcels_Rc;
CREATE TABLE Parcels_Rc
 (
	Parcels_RC_PK			bigint, 
	propertySituationId		bigint, 
	"order"				Integer, 
	polWa				Character varying (20), 
	surfaceNotTaxable		bigint, 
	surfaceTaxable			bigint, 
	surfaceVerif			Character varying (2), 
	soilIndex			bigint, 
	soilRent			Character varying (10), 
	cadastralIncomePerSurface	bigint, 
	cadastralIncomePerSurfaceOtherDi	bigint, 
	numberCadastralIncome		bigint, 
	charCadastralIncome		Character varying (4), 
	cadastralIncome			bigint, 
	dateEndExoneration		date, 
	decrete				Character varying (40), 
	dateSituation			date
);

DROP TABLE IF EXISTS ParcelsStreets;
CREATE TABLE ParcelsStreets
 (
	Street_UID			serial, 
	nisCom				bigint, 
	street_situation		Character varying (200), 
	street_translation		Character varying (200), 
	street_code			bigint
);

DROP SEQUENCE IF EXISTS public.oid;
CREATE SEQUENCE public.oid
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;


DROP TABLE IF EXISTS Owners_imp;
CREATE TABLE Owners_imp
 (
	propertySituationIdf		Bigint, 
	"order"			        Integer, 
	partyType			Integer, 
	OwnerRight			Character varying (120), 
	right_trad			Character varying (102), 
	managedBy			Character varying (4), 
	owner_officialId		Character varying (30), 
	owner_name			Character varying (400), 
	owner_firstname			Character varying (180), 
	owner_birthdate			date, 
	owner_country			Character varying (4), 
	owner_zipCode			Character varying (30), 
	owner_municipality_fr		Character varying (100), 
	owner_municipality_nl		Character varying (100), 
	owner_street_fr			Character varying (300), 
	owner_street_nl			Character varying (300), 
	owner_number			Character varying (20), 
	owner_boxNumber			Character varying (20), 
	partner_officialId		Character varying (30), 
	partner_name			Character varying (400), 
	partner_firstname		Character varying (180), 
	partner_birthdate		date, 
	partner_country			Character varying (4), 
	partner_zipCode			Character varying (30), 
	partner_municipality_fr		Character varying (100), 
	partner_municipality_nl		Character varying (100), 
	partner_street_fr		Character varying (300), 
	partner_street_nl		Character varying (300), 
	partner_number			Character varying (20), 
	partner_boxNumber		Character varying (20), 
	coOwner				Character varying (120), 
	anonymousOwner			Character varying (120), 
	dateSituation			date,
	divcad				Bigint
);

DROP TABLE IF EXISTS Parcels_imp;
DROP SEQUENCE IF EXISTS public.pid;

CREATE SEQUENCE public.pid
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE TABLE Parcels_imp
 (
	propertySituationIdf		Bigint, 
	divCad				Bigint, 
	section				Character varying (2), 
	primaryNumber			Integer, 
	bisNumber			Character varying (6), 
	exponentLetter			Character varying (2), 
	exponentNumber			Character varying (6), 
	partNumber			Character varying (10), 
	capakey				Character varying (34), 
	"order"				Integer,
	nature				Integer, 
	descriptPrivate			Character varying (100), 
	block				Character varying (20), 
	floor				Character varying (20), 
	floorSituation			Character varying (60), 
	crossDetail			Character varying (60), 
	matUtil				Character varying (60), 
	notTaxedMatUtil			Character varying (10), 
	nisCom				Bigint, 
	street_situation		Character varying (200), 
	street_translation		Character varying (200), 
	street_code			Bigint, 
	number				Character varying (20), 
	polWa				Character varying (20), 
	surfaceNotTaxable		Bigint, 
	surfaceTaxable			Bigint, 
	surfaceVerif			Character varying (2), 
	constructionYear		Character varying (8), 
	soilIndex			Bigint, 
	soilRent			Character varying (10), 
	cadastralIncomePerSurface	Bigint, 
	cadastralIncomePerSurfaceOtherDi			Bigint, 
	numberCadastralIncome		Bigint, 
	charCadastralIncome		Character varying (4), 
	cadastralIncome			Bigint, 
	dateEndExoneration		date, 
	decrete				Character varying (40), 
	constructionIndication		Integer, 
	constructionType		Character varying (40), 
	floorNumberAboveground		Character varying (510), 
	garret				Character varying (2), 
	physModYear			Character varying (8), 
	constructionQuality		Character varying (2), 
	garageNumber			Integer, 
	centralHeating			Character varying (2), 
	bathroomNumber			Integer, 
	housingUnitNumber		Integer, 
	placeNumber			Integer, 
	builtSurface			Bigint, 
	usedSurface			Bigint, 
	dateSituation			date
);
