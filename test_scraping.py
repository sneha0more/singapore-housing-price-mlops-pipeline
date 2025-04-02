from housing_etl.scraping import scrape_edgeprop_properties

df = scrape_edgeprop_properties()

print(f"\n✅ Scraped {len(df)} listings.")
print(df.head())
