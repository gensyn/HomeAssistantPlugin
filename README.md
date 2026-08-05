<div align="center">

# 🏠 Home Assistant Plugin

### For [StreamController](https://github.com/StreamController/StreamController)

**Control your Home Assistant instance directly from your StreamDeck**

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Compatible-41BDF5?logo=homeassistant)](https://www.home-assistant.io/)
[![StreamController](https://img.shields.io/badge/StreamController-Plugin-green)](https://github.com/StreamController/StreamController)

[Features](#-features) • [Installation](#-installation) • [Documentation](#-documentation) • [Examples](#-examples) • [Support](#-support)

---

</div>

> **This is not an official plugin** - I have no affiliation with Home Assistant, StreamDeck, or StreamController.

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Features](#-features)
- [Installation](#-installation)
- [Documentation](#-documentation)
  - [Plugin Settings](#-plugin-settings)
  - [Perform Action](#-perform-action)
  - [Show Icon](#-show-icon)
  - [Show Text](#-show-text)
  - [Level Dial](#-level-dial)
- [Examples](#-examples)
- [Support](#-support)

## ✅ Prerequisites

> Before using this plugin, ensure the following requirements are met:

- **WebSocket API**: The `websocket_api` component must be present in your `configuration.yaml`
  - Remember to restart Home Assistant after updating your configuration
  
- **Long-Lived Access Token**: Required to authenticate with Home Assistant
  1. Navigate to your user profile in Home Assistant
  2. Click on the **Security** tab
  3. Scroll to the bottom and create a new _Long-Lived Access Token_
  4. **Copy the token immediately** - you won't be able to retrieve it later!

> **Security Notice**: Keep your Home Assistant URL and access token secure. Anyone with this information can access and control your Home Assistant instance if it's exposed to the internet.

## ✨ Features

### 🎬 Perform an Action
- Execute any Home Assistant action/service
- Provide custom parameters for actions
- Actions trigger on `key_down` (button press) by default
- Use the built-in **Event Assigner** to customize behavior:
  - Map different events to `key_down`
  - Disable `key_down` by mapping it to `None`

### 🎨 Show an Icon
- Display entity icons or custom icons from [Material Design Icons](https://pictogrammers.com/library/mdi/) as well as images and GIFs
- Customize icon appearance:
  - 🎨 Color
  - 📏 Scale
  - 🌫️ Opacity
- Customize image appearance:
  - 📏 Scale
- **Dynamic customization** based on state or attribute values
- Automatic updates when entity state changes

### 📝 Show Text
- Display entity state, attributes, or custom text
- Real-time updates when entity state changes
- Full customization options:
  - 📍 Position
  - 📐 Text size
  - 🎨 Text color
  - 🔲 Outline size and color
- Show unit of measurement (with optional line breaks)
- **Dynamic customization** based on state or attribute values

### 🎛️ Level Dial
- Control entity levels with a Stream Deck Plus dial
- Supports lights (brightness), fans (speed), covers (position), and media players (volume)
- Turn CW/CCW to adjust level, press to toggle on/off
- Displays current level as a percentage on the touchscreen
- Shows the entity's icon with on/off color tinting
- Configurable step size, display name, and command batching delay
- **Dynamic customization** of icon and color based on state or attribute values

## 📥 Installation

1. Install the plugin through StreamController's plugin manager
2. Configure your Home Assistant connection in the plugin settings
3. Start adding actions to your StreamDeck buttons!

## 📖 Documentation

### ⚙️ Plugin Settings

**Opening the Settings:**
1. Open your StreamController settings
2. Navigate to the **Plugins** tab
3. Find **Home Assistant** in the list
4. Click **Open Settings**

<div align="center">

![Plugin settings](assets/connection_settings.png)

</div>

**Configuration:**
- Enter your Home Assistant URL
- Provide your long-lived access token
- For self-signed certificates, disable **Verify certificate**

> The plugin automatically attempts to connect once all information is entered. If the connection fails or is lost, it will retry every 10 seconds.

---

### 🎬 Perform Action

Execute Home Assistant actions directly from your StreamDeck.

<div align="center">

![Action settings service](assets/perform_action.png)

</div>

**Configuration:**
- **Action**: Select the Home Assistant action to perform
- **Entity** (optional): Choose the target entity if required
- **Parameters** (optional): Configure action parameters
  - Only checked parameters are sent with the action
  - List shows all possible parameters (not all may be supported by the entity)

---

### 🎨 Show Icon

Display dynamic icons based on Home Assistant entity data.

<div align="center">

![Action settings icon](assets/show_icon.png)

</div>

**Configuration:**
- **Entity**: Select the Home Assistant entity
- **Icon**: 
  - Leave empty to use the entity's default icon
  - Enter a [Material Design Icon](https://pictogrammers.com/library/mdi/) name to override
- **Customization**: Adjust color, scale, and opacity

#### 🎯 Icon Customization

Create conditional icon appearances based on entity states.

**Creating a Customization:**
1. Click the ![Add customization](assets/action_customize_add.png) button in the **Customize** row
2. Define a condition (state or attribute value)
3. Configure icon changes when the condition is met

<div align="center">

![Icon customization dialog](assets/show_icon_customize.png)

</div>

**Managing Customizations:**

<div align="center">

![Icon customizations list](assets/show_icon_customizations.png)

</div>

> **Cascading Behavior**: Customizations are evaluated in order from top to bottom. When multiple conditions match, the last matching customization wins. In the example above, both conditions are met, but the icon displayed is `lamp` from the second customization.

**Features:**
- ✏️ Edit, delete, and reorder customizations
- 👁️ View current entity value for reference
- ✅ Only checked settings are applied

---

### 📝 Show Text

Display dynamic text based on Home Assistant entity data.

<div align="center">

![Action settings text](assets/show_text.png)

</div>

**Configuration:**
- **Entity**: Select the Home Assistant entity
- **Position**: Choose where the text appears on the key
- **Attribute**: Select what to display:
  - Entity state
  - Specific attribute value
- **Rounding**: 
  - Enable to round numeric values
  - Set decimal precision
- **Styling**:
  - Text size and color
  - Outline size and color
- **Unit of Measurement** (if available):
  - Show/hide unit
  - Optional line break between value and unit

#### 🎯 Text Customization

Create conditional text appearances based on entity states.

**Creating a Customization:**
1. Click the ![Add customization](assets/action_customize_add.png) button in the **Customize** row
2. Define a condition (state or attribute value)
3. Configure text changes when the condition is met

<div align="center">

![Text customization dialog](assets/show_text_customize.png)

</div>

**Managing Customizations:**

<div align="center">

![Text customizations list](assets/show_text_customizations.png)

</div>

> **Cascading Behavior**: Like icon customizations, text customizations are evaluated in order. The last matching customization sets the final value. In the example above, only the second customization matches, setting text size to 12.

**Advanced Features:**

- **Custom Text**: Select `custom_text` as an attribute to display custom messages
  - Use `%s` as a placeholder for the original value
  - Use `\n` for line breaks
  - **Example**: For a temperature attribute, use `%s\n°C` to display:
    ```
    23.5
    °C
    ```
  - Perfect for creating custom translations!

**Features:**
- ✏️ Edit, delete, and reorder customizations
- 👁️ View current entity value for reference
- ✅ Only checked settings are applied

---

### 🎛️ Level Dial

Control Home Assistant entity levels directly from a Stream Deck Plus dial.

**Configuration:**
- **Entity**: Select the Home Assistant entity to control
- **Display name**: Custom label for the touchscreen (defaults to entity's friendly name)
- **Step size**: Percentage change per dial tick (1–50)
- **Batch delay**: Milliseconds to wait for additional turns before sending the command (0–500)
  - Prevents flooding your network with rapid dial turns

**Supported Domains:**
- **Lights**: Adjusts brightness (0–255 mapped to percentage)
- **Fans**: Adjusts speed percentage
- **Covers**: Adjusts position
- **Media players**: Adjusts volume

**Controls:**
- **Turn CW/CCW**: Increase/decrease level
- **Press**: Toggle entity on/off

**Behavior:**
- Displays the target percentage immediately on each tick, before Home Assistant confirms
- Batches rapid turns into a single command to avoid mesh/network flooding
- Fine-grained 1% steps below 10% for precise low-level control
- Shows the entity's icon from Home Assistant with color tinting (on/off)

#### 🎯 Level Dial Customization

Create conditional icon and color appearances based on entity states.

**Creating a Customization:**
1. Click the ![Add customization](assets/action_customize_add.png) button in the **Customize** row
2. Define a condition (state or attribute value)
3. Configure icon and/or color changes when the condition is met

**Features:**
- ✏️ Edit, delete, and reorder customizations
- 👁️ View current entity value for reference
- ✅ Only checked settings are applied

> **Cascading Behavior**: Like icon and text customizations, level dial customizations are evaluated in order. The last matching customization sets the final icon and color.

---

## 🎯 Examples

### 🌤️ Weather Display

<div align="center">

![Weather button](assets/example_1.png)

</div>

**Setup:**
- Uses **Show Text** action with a weather entity
- Displays current weather information directly on your StreamDeck

---

### 🔘 Toggle Button

<div align="center">

![Boolean toggle button](assets/example_2.gif)

</div>

**Setup:**
- **Show Icon**: Display icon with customization
  - Changes color to yellow when `input_boolean` is `on`
- **Perform Action**: Toggle the `input_boolean` state
- Both actions use the same entity

---

### 🎵 Media Player Control

<div align="center">

![Media player button](assets/example_3.gif)

</div>

**Setup:**
- **Show Icon**: Dynamic play/pause icon
  - Shows `play` icon by default
  - Shows `pause` icon when media is playing
- **Perform Action**: Execute `media_play_pause` action
- **Show Text** (×2): Display media title and artist
- All actions use the same media player entity

---

### 💨 Air Quality Monitor

<div align="center">

![Air quality button](assets/example_4.gif)

</div>

**Setup:**
- **Show Text**: Display CO₂ sensor value
  - Includes unit of measurement
  - Line break between value and unit
- **Show Icon**: Ventilator icon at 50% opacity
- **Perform Action**: Toggle ventilator on/off
- Uses both CO₂ sensor and ventilator entities

---

## 🚀 Roadmap

Currently, all planned features have been implemented! Have a suggestion? [Open an issue](https://github.com/gensyn/HomeAssistantPlugin/issues)!

---

## 🆘 Support

### Having Issues?

If you encounter any problems or have questions:

1. 📖 Check the [documentation](#-documentation) above
2. 🔍 Search [existing issues](https://github.com/gensyn/HomeAssistantPlugin/issues)
3. 🐛 [Open a new issue](https://github.com/gensyn/HomeAssistantPlugin/issues/new) with:
   - Detailed description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)

### Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit pull requests


---

## ⭐ Support

If you find HomeAssistantPlugin useful, please consider giving it a star on GitHub! It helps others discover the project. 

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/M5G61ZZY8D)
