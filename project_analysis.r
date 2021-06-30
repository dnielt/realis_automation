library(dplyr)
library(tidyverse)
library(zoo)
library(scales)

current_path = dirname(rstudioapi::getSourceEditorContext()$path)
setwd(paste0(current_path, '/data'))

all_files = list.files(pattern = "\\.csv")
raw = data.frame()

for (file in all_files)
{
  temp = read_csv(file)
  raw = bind_rows(raw, temp)
}

#sample_n(raw, 3)
result = raw %>%
  rename(project_name = `Project Name`,
         price_transacted = `Transacted Price ($)`,
         area_sqft = `Area (SQFT)`,
         area_sqm = `Area (SQM)`,
         price_psf = `Unit Price ($ PSF)`,
         sale_date = `Sale Date`,
         address = Address,
         sale_type = `Type of Sale`,
         area_type = `Type of Area`,
         price_psm = `Unit Price ($ PSM)`,
         price_nett = `Nett Price($)`,
         property_type = `Property Type`,
         no_units = `Number of Units`,
         tenure = Tenure,
         completion_date = `Completion Date`,
         buyer_indicator = `Purchaser Address Indicator`,
         postal_code = `Postal Code`,
         postal_district = `Postal District`,
         postal_sector = `Postal Sector`,
         planning_region = `Planning Region`,
         planning_area = `Planning Area`)

#sample_n(as.data.frame(result), 3)

result = result %>%
  mutate(
    id = row_number(),
    project_name = as.factor(project_name),
    address_road = ifelse(grepl("#", address), 
                          gsub(" #.*", "", address), address),
    address_unit = ifelse(!grepl("#", address), NA, gsub(".*#", "#", address)),
    address_floor = ifelse(!is.na(address_unit),
                           as.numeric(gsub("^#(.*)-.*", "\\1", address_unit)),
                           NA),
    address_stack = ifelse(!is.na(address_unit),
                           as.numeric(gsub("^#.*-(.*)", "\\1", address_unit)),
                           NA), #\\1 means keep the first group (.*)
    sale_date = as.Date(sale_date, "%d %b %Y"),
    sale_month = as.yearmon(sale_date),
    sale_type = as.factor(sale_type),
    area_type = as.factor(area_type),
    tenure_is_freehold = ifelse(grepl("Freehold", tenure), 1, 0),
    tenure_leasehold_years = 
      ifelse(grepl("yrs", tenure), gsub(" yrs.*", "", tenure), NA),
    tenure_leasehold_years = as.numeric(tenure_leasehold_years),
    tenure_leasehold_start = 
      ifelse(grepl("yrs", tenure), gsub(".*from ", "", tenure), NA),
    tenure_leasehold_start = as.Date(tenure_leasehold_start, "%d/%m/%Y"),
    tenure_used = as.numeric(difftime(Sys.Date(), tenure_leasehold_start)/365),
    tenure_remaining = tenure_leasehold_years - tenure_used,
    market_segment = "OCR",
    market_segment =
      ifelse(postal_district %in% c("09", "10", "11"), "CCR", market_segment),
    market_segment = 
      ifelse(planning_area %in% c("Downtown Core", "Southern Islands"), 
             "CCR", market_segment),
    market_segment = 
      ifelse(planning_region == "Central Region" & market_segment != "CCR",
             "RCR", market_segment),
    market_segment = as.factor(market_segment),
    postal_district = as.factor(postal_district)
  )


# only keep current owners
result = result %>%
  #filter(sale_type == "Resale") %>%
  group_by(address) %>%
  slice(which.max(as.Date(sale_date, "%d %b %Y")))

result = as.data.frame(result)

hist(result$price_psf, breaks = 100, freq=TRUE)

final = result %>%
  summarise("mean psf" = mean(price_psf), 
            "median psf" = median(price_psf))

result[which.min(result$price_psf),]
result[which.max(result$price_psf),]


#plot by floor
result2 = result %>%
  filter(sale_type == "New Sale") %>%
  group_by(address_floor) %>%
  summarise(mean(price_psf))

plot(result2)


# line chart for B1/B2 units by floor
result %>%
  filter(area_sqft == 678.13) %>%
  #filter(area_sqft == 699.66) %>%
  group_by(address_floor) %>% 
  summarise(mean=mean(price_transacted)) %>%
  ggplot(aes(x=address_floor, y=mean)) +
  geom_line() +
  scale_y_continuous(label=comma)
  

# line chart for B1/B2 unit PSF over time
result %>%
  filter(area_sqft >= 600 | area_sqft <= 900) %>%
  #group_by(sale_month, area_sqft) %>% 
  #summarise(mean=mean(price_transacted)) %>%
  ggplot(aes(x=sale_date, y=price_psf)) +
  geom_line() +
  scale_y_continuous(label=comma)


# filter only 4BR, see unit PSF over time
result %>%
  filter(area_sqft >= 1200,
         area_sqft <= 1400) %>%
  #group_by(sale_month, area_sqft) %>% 
  #summarise(mean=median(price_psf)) %>%
  ggplot(aes(x=price_psf, fill=factor(sale_month))) +
  geom_histogram(binwidth = 5) +
  scale_y_continuous(label=comma) +
  scale_x_continuous(label=comma, breaks=seq(1000,1700,50)) +
  geom_vline(xintercept = 1333) +
  theme_bw()


