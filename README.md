# Activity 3 BluePrints

## Overview
Design UI blueprints for an application. 
  - Ensure they are consistent and professional
  - Display how to navigate
  - Every UI element will connect to the database
  - Document screen transitions

## Design Consistency
  - Fixed window size  (1280 x 800)
  - Same font (Segoe UI)
  - Primary color (#2C3E50) dark blue-gray
  - Secondary color (#3498DB) action buttons color
  - Accent color (#E74C3C) alerts/low stock
  - Background color (#F5F5F5) light gray

## Navigation Structure
Show how users move between screens.
  - Basic flow: Login -> Dashboard -> Other Modules
  - Each section will branch to more detailed screens
  - Every transition is shown and labeled

## Core Screens to Blueprint
  - Dashboard:
      - Overview of business performance
      - Display metrics (total sales, orders today, etc.)
  - Products:
      - List of product info (price, quantity, etc.)
      - View to add/edit products
      - Display the actual product and its inventory data
  - Inventory:
      - Overview of stock levels
      - Display quantity, status, reorder levels, etc.
      - Screen for receiving stock (incoming inventory)
  - Orders + Payments:
      - Orders list (ID, customer, total, etc)
      - Screen for payments (total amount, payment method, payment status, etc.)

## Screen Transitions
- Examples:
  - Dashboard -> Products (click button)
  - Orders -> New Order -> Payment -> Confirmation

## Data Mapping
Elements are connected to a database field.
- Examples:
  - Total Sales = Orders.TotalAmount
  - Orders Today = Orders.OrderDate
