-- Commodity taxonomy tree
-- Recreates the commodity_tree and article_tags tables from scratch.
-- Run this AFTER sql/ingestion/articles.sql (article_tags references articles).
--
-- Table structure matches the live DB:
--   level 1 = sector            (Energy, Agriculture, Metals)
--   level 2 = commodity_group   (Natural Gas, Oil, Grains ...)
--   level 3 = classification    (European Gas, Global Crude ...)
--   level 4 = instrument        (TTF, Brent, Corn ...)

CREATE TABLE dbo.commodity_tree (
    id                       INT           IDENTITY(1,1) PRIMARY KEY,
    parent_id                INT           NULL REFERENCES dbo.commodity_tree(id),
    level                    TINYINT       NOT NULL,          -- 1-4
    name                     VARCHAR(100)  NOT NULL,
    full_path                VARCHAR(500)  NOT NULL,          -- e.g. Energy::Natural Gas::European Gas::TTF
    sector                   VARCHAR(100)  NOT NULL,
    commodity_group          VARCHAR(100)  NULL,
    commodity_classification VARCHAR(100)  NULL,
    commodity_name           VARCHAR(100)  NULL,
    is_leaf                  BIT           NOT NULL DEFAULT 0,
    is_active                BIT           NOT NULL DEFAULT 1,
    sort_order               INT           NOT NULL DEFAULT 0,
    created_at               DATETIME2     NOT NULL DEFAULT GETUTCDATE(),
    updated_at               DATETIME2     NOT NULL DEFAULT GETUTCDATE()
);

CREATE INDEX ix_commodity_tree_lookup
    ON dbo.commodity_tree (sector, commodity_group, commodity_classification, commodity_name, is_active);

-- article_tags: links articles to taxonomy nodes
CREATE TABLE dbo.article_tags (
    id                INT  IDENTITY(1,1) PRIMARY KEY,
    article_id        INT  NOT NULL REFERENCES dbo.articles(id) ON DELETE CASCADE,
    commodity_tree_id INT  NOT NULL REFERENCES dbo.commodity_tree(id),
    CONSTRAINT uq_article_tag UNIQUE (article_id, commodity_tree_id)
);

-- ── Seed data ─────────────────────────────────────────────────────────────────
-- Level 1 — sectors
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order) VALUES
(NULL, 1, 'Energy',      'Energy',      'Energy',      NULL, NULL, NULL, 0, 10),
(NULL, 1, 'Agriculture', 'Agriculture', 'Agriculture', NULL, NULL, NULL, 0, 20),
(NULL, 1, 'Metals',      'Metals',      'Metals',      NULL, NULL, NULL, 0, 30);

-- Level 2 — groups  (parent_id references level-1 rows above by their inserted IDs)
-- Energy groups
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 2, 'Natural Gas',      'Energy::Natural Gas',      'Energy', 'Natural Gas',      NULL, NULL, 0, 12 FROM dbo.commodity_tree WHERE full_path = 'Energy';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 2, 'LNG',              'Energy::LNG',              'Energy', 'LNG',              NULL, NULL, 0, 15 FROM dbo.commodity_tree WHERE full_path = 'Energy';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 2, 'Oil',              'Energy::Oil',              'Energy', 'Oil',              NULL, NULL, 0, 16 FROM dbo.commodity_tree WHERE full_path = 'Energy';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 2, 'Refined Products', 'Energy::Refined Products', 'Energy', 'Refined Products', NULL, NULL, 0, 18 FROM dbo.commodity_tree WHERE full_path = 'Energy';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 2, 'Coal',             'Energy::Coal',             'Energy', 'Coal',             NULL, NULL, 0, 19 FROM dbo.commodity_tree WHERE full_path = 'Energy';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 2, 'Power',            'Energy::Power',            'Energy', 'Power',            NULL, NULL, 0, 10 FROM dbo.commodity_tree WHERE full_path = 'Energy';

-- Agriculture groups
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 2, 'Grains',      'Agriculture::Grains',      'Agriculture', 'Grains',      NULL, NULL, 0, 20 FROM dbo.commodity_tree WHERE full_path = 'Agriculture';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 2, 'Oilseeds',    'Agriculture::Oilseeds',    'Agriculture', 'Oilseeds',    NULL, NULL, 0, 22 FROM dbo.commodity_tree WHERE full_path = 'Agriculture';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 2, 'Softs',       'Agriculture::Softs',       'Agriculture', 'Softs',       NULL, NULL, 0, 23 FROM dbo.commodity_tree WHERE full_path = 'Agriculture';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 2, 'Fertilizers', 'Agriculture::Fertilizers', 'Agriculture', 'Fertilizers', NULL, NULL, 0, 25 FROM dbo.commodity_tree WHERE full_path = 'Agriculture';

-- Metals groups
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 2, 'Base Metals',    'Metals::Base Metals',    'Metals', 'Base Metals',    NULL, NULL, 0, 30 FROM dbo.commodity_tree WHERE full_path = 'Metals';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 2, 'Precious Metals','Metals::Precious Metals','Metals', 'Precious Metals',NULL, NULL, 0, 33 FROM dbo.commodity_tree WHERE full_path = 'Metals';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 2, 'Ferrous',        'Metals::Ferrous',        'Metals', 'Ferrous',        NULL, NULL, 0, 34 FROM dbo.commodity_tree WHERE full_path = 'Metals';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 2, 'Battery Metals', 'Metals::Battery Metals', 'Metals', 'Battery Metals', NULL, NULL, 0, 35 FROM dbo.commodity_tree WHERE full_path = 'Metals';

-- Level 3 — classifications
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'European Gas',        'Energy::Natural Gas::European Gas',        'Energy', 'Natural Gas',      'European Gas',        NULL, 0, 12 FROM dbo.commodity_tree WHERE full_path = 'Energy::Natural Gas';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'US Gas',              'Energy::Natural Gas::US Gas',              'Energy', 'Natural Gas',      'US Gas',              NULL, 0, 14 FROM dbo.commodity_tree WHERE full_path = 'Energy::Natural Gas';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'LNG Spot',            'Energy::LNG::LNG Spot',                    'Energy', 'LNG',              'LNG Spot',            NULL, 0, 15 FROM dbo.commodity_tree WHERE full_path = 'Energy::LNG';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'Global Crude',        'Energy::Oil::Global Crude',                'Energy', 'Oil',              'Global Crude',        NULL, 0, 16 FROM dbo.commodity_tree WHERE full_path = 'Energy::Oil';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'Middle Distillates',  'Energy::Refined Products::Middle Distillates','Energy','Refined Products','Middle Distillates',  NULL, 0, 18 FROM dbo.commodity_tree WHERE full_path = 'Energy::Refined Products';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'Thermal Coal',        'Energy::Coal::Thermal Coal',               'Energy', 'Coal',             'Thermal Coal',        NULL, 0, 19 FROM dbo.commodity_tree WHERE full_path = 'Energy::Coal';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'European Power',      'Energy::Power::European Power',            'Energy', 'Power',            'European Power',      NULL, 0, 10 FROM dbo.commodity_tree WHERE full_path = 'Energy::Power';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'Wheat',               'Agriculture::Grains::Wheat',               'Agriculture','Grains',      'Wheat',               NULL, 0, 20 FROM dbo.commodity_tree WHERE full_path = 'Agriculture::Grains';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'Corn',                'Agriculture::Grains::Corn',                'Agriculture','Grains',      'Corn',                NULL, 0, 21 FROM dbo.commodity_tree WHERE full_path = 'Agriculture::Grains';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'Soy Complex',         'Agriculture::Oilseeds::Soy Complex',       'Agriculture','Oilseeds',   'Soy Complex',         NULL, 0, 22 FROM dbo.commodity_tree WHERE full_path = 'Agriculture::Oilseeds';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'Sugar',               'Agriculture::Softs::Sugar',                'Agriculture','Softs',      'Sugar',               NULL, 0, 23 FROM dbo.commodity_tree WHERE full_path = 'Agriculture::Softs';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'Coffee',              'Agriculture::Softs::Coffee',               'Agriculture','Softs',      'Coffee',              NULL, 0, 24 FROM dbo.commodity_tree WHERE full_path = 'Agriculture::Softs';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'Nitrogen',            'Agriculture::Fertilizers::Nitrogen',       'Agriculture','Fertilizers','Nitrogen',            NULL, 0, 25 FROM dbo.commodity_tree WHERE full_path = 'Agriculture::Fertilizers';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'Copper',              'Metals::Base Metals::Copper',              'Metals','Base Metals',     'Copper',              NULL, 0, 30 FROM dbo.commodity_tree WHERE full_path = 'Metals::Base Metals';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'Aluminium',           'Metals::Base Metals::Aluminium',           'Metals','Base Metals',     'Aluminium',           NULL, 0, 31 FROM dbo.commodity_tree WHERE full_path = 'Metals::Base Metals';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'Nickel',              'Metals::Base Metals::Nickel',              'Metals','Base Metals',     'Nickel',              NULL, 0, 32 FROM dbo.commodity_tree WHERE full_path = 'Metals::Base Metals';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'Gold',                'Metals::Precious Metals::Gold',            'Metals','Precious Metals', 'Gold',                NULL, 0, 33 FROM dbo.commodity_tree WHERE full_path = 'Metals::Precious Metals';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'Steel Raw Materials', 'Metals::Ferrous::Steel Raw Materials',     'Metals','Ferrous',         'Steel Raw Materials', NULL, 0, 34 FROM dbo.commodity_tree WHERE full_path = 'Metals::Ferrous';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 3, 'Lithium',             'Metals::Battery Metals::Lithium',          'Metals','Battery Metals',  'Lithium',             NULL, 0, 35 FROM dbo.commodity_tree WHERE full_path = 'Metals::Battery Metals';

-- Level 4 — instruments (is_leaf = 1)
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'TTF',               'Energy::Natural Gas::European Gas::TTF',               'Energy','Natural Gas',     'European Gas',       'TTF',               1, 12 FROM dbo.commodity_tree WHERE full_path = 'Energy::Natural Gas::European Gas';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'NBP',               'Energy::Natural Gas::European Gas::NBP',               'Energy','Natural Gas',     'European Gas',       'NBP',               1, 13 FROM dbo.commodity_tree WHERE full_path = 'Energy::Natural Gas::European Gas';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'Henry Hub',         'Energy::Natural Gas::US Gas::Henry Hub',               'Energy','Natural Gas',     'US Gas',             'Henry Hub',         1, 14 FROM dbo.commodity_tree WHERE full_path = 'Energy::Natural Gas::US Gas';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'JKM',               'Energy::LNG::LNG Spot::JKM',                          'Energy','LNG',             'LNG Spot',           'JKM',               1, 15 FROM dbo.commodity_tree WHERE full_path = 'Energy::LNG::LNG Spot';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'Brent',             'Energy::Oil::Global Crude::Brent',                    'Energy','Oil',             'Global Crude',       'Brent',             1, 16 FROM dbo.commodity_tree WHERE full_path = 'Energy::Oil::Global Crude';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'WTI',               'Energy::Oil::Global Crude::WTI',                      'Energy','Oil',             'Global Crude',       'WTI',               1, 17 FROM dbo.commodity_tree WHERE full_path = 'Energy::Oil::Global Crude';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'Diesel',            'Energy::Refined Products::Middle Distillates::Diesel', 'Energy','Refined Products','Middle Distillates', 'Diesel',            1, 18 FROM dbo.commodity_tree WHERE full_path = 'Energy::Refined Products::Middle Distillates';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'API2',              'Energy::Coal::Thermal Coal::API2',                    'Energy','Coal',            'Thermal Coal',       'API2',              1, 19 FROM dbo.commodity_tree WHERE full_path = 'Energy::Coal::Thermal Coal';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'UK Baseload',       'Energy::Power::European Power::UK Baseload',           'Energy','Power',           'European Power',     'UK Baseload',       1, 10 FROM dbo.commodity_tree WHERE full_path = 'Energy::Power::European Power';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'German Baseload',   'Energy::Power::European Power::German Baseload',       'Energy','Power',           'European Power',     'German Baseload',   1, 11 FROM dbo.commodity_tree WHERE full_path = 'Energy::Power::European Power';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'MATIF Wheat',       'Agriculture::Grains::Wheat::MATIF Wheat',             'Agriculture','Grains',    'Wheat',              'MATIF Wheat',       1, 20 FROM dbo.commodity_tree WHERE full_path = 'Agriculture::Grains::Wheat';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'Corn',              'Agriculture::Grains::Corn::Corn',                     'Agriculture','Grains',    'Corn',               'Corn',              1, 21 FROM dbo.commodity_tree WHERE full_path = 'Agriculture::Grains::Corn';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'Soybeans',          'Agriculture::Oilseeds::Soy Complex::Soybeans',        'Agriculture','Oilseeds', 'Soy Complex',        'Soybeans',          1, 22 FROM dbo.commodity_tree WHERE full_path = 'Agriculture::Oilseeds::Soy Complex';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'Raw Sugar',         'Agriculture::Softs::Sugar::Raw Sugar',                'Agriculture','Softs',    'Sugar',              'Raw Sugar',         1, 23 FROM dbo.commodity_tree WHERE full_path = 'Agriculture::Softs::Sugar';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'Arabica Coffee',    'Agriculture::Softs::Coffee::Arabica Coffee',          'Agriculture','Softs',    'Coffee',             'Arabica Coffee',    1, 24 FROM dbo.commodity_tree WHERE full_path = 'Agriculture::Softs::Coffee';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'Urea',              'Agriculture::Fertilizers::Nitrogen::Urea',            'Agriculture','Fertilizers','Nitrogen',          'Urea',              1, 25 FROM dbo.commodity_tree WHERE full_path = 'Agriculture::Fertilizers::Nitrogen';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'Copper',            'Metals::Base Metals::Copper::Copper',                 'Metals','Base Metals',   'Copper',             'Copper',            1, 30 FROM dbo.commodity_tree WHERE full_path = 'Metals::Base Metals::Copper';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'Aluminium',         'Metals::Base Metals::Aluminium::Aluminium',           'Metals','Base Metals',   'Aluminium',          'Aluminium',         1, 31 FROM dbo.commodity_tree WHERE full_path = 'Metals::Base Metals::Aluminium';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'Nickel',            'Metals::Base Metals::Nickel::Nickel',                 'Metals','Base Metals',   'Nickel',             'Nickel',            1, 32 FROM dbo.commodity_tree WHERE full_path = 'Metals::Base Metals::Nickel';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'Gold',              'Metals::Precious Metals::Gold::Gold',                 'Metals','Precious Metals','Gold',              'Gold',              1, 33 FROM dbo.commodity_tree WHERE full_path = 'Metals::Precious Metals::Gold';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'Iron Ore',          'Metals::Ferrous::Steel Raw Materials::Iron Ore',      'Metals','Ferrous',       'Steel Raw Materials','Iron Ore',          1, 34 FROM dbo.commodity_tree WHERE full_path = 'Metals::Ferrous::Steel Raw Materials';
INSERT INTO dbo.commodity_tree (parent_id, level, name, full_path, sector, commodity_group, commodity_classification, commodity_name, is_leaf, sort_order)
SELECT id, 4, 'Lithium Carbonate', 'Metals::Battery Metals::Lithium::Lithium Carbonate',  'Metals','Battery Metals', 'Lithium',           'Lithium Carbonate', 1, 35 FROM dbo.commodity_tree WHERE full_path = 'Metals::Battery Metals::Lithium';

-- Mark all level-4 nodes as leaves (already set above), ensure parent is_leaf stays 0
UPDATE dbo.commodity_tree SET is_leaf = 1 WHERE level = 4;
