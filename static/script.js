// AI Pamphlet Generator - JavaScript

let currentFilename = '';
let originalImageData = '';
let customImageData = '';
let layoutBaseImageData = '';
let finalImageData = '';
let regenerationCount = 0;
let isRegenerating = false;
let latestKeyFeatures = [];
let latestTextContent = null;
let currentRemovals = {
    headline: false,
    tagline: false,
    description: false,
    call_to_action: false,
    custom: false
};
let customTextLines = [];
let currentEdits = {
    size: { width: 1200, height: 1600 },
    layout: 'centered',
    textPlacement: 'top',
    backgroundOpacity: 80,
    headlineFont: 'Arial-Bold',
    headlineSize: 72,
    headlineColor: '#ffffff',
    bodyFont: 'Arial',
    bodySize: 28,
    bodyColor: '#ffffff',
    ctaBgColor: '#ff6464',
    ctaTextColor: '#ffffff',
    imageFilter: 'none',
    filterIntensity: 50,
    imageCrop: 'none',
    imagePosition: 'center',
    shadowIntensity: 0,
    borderRadius: 12,
    textShadow: 0,
    overallBrightness: 100
};

// DOM Elements
const form = document.getElementById('pamphletForm');
const resultsContainer = document.getElementById('resultsContainer');
const loadingOverlay = document.getElementById('loadingOverlay');
const pamphletImage = document.getElementById('pamphletImage');
const textContent = document.getElementById('textContent');
const generateBtn = document.getElementById('generateBtn');
const previewOverlay = document.getElementById('previewOverlay');
const previewHeadline = document.getElementById('previewHeadline');
const previewTagline = document.getElementById('previewTagline');
const previewDescription = document.getElementById('previewDescription');
const previewCTA = document.getElementById('previewCTA');
const previewCustom = document.getElementById('previewCustom');
const overlayContent = document.getElementById('overlayContent');
const previewContainer = document.querySelector('.preview-container');
const hideHeadlineToggle = document.getElementById('toggleHeadline');
const hideTaglineToggle = document.getElementById('toggleTagline');
const hideDescriptionToggle = document.getElementById('toggleDescription');
const hideCtaToggle = document.getElementById('toggleCTA');
const hideCustomToggle = document.getElementById('toggleCustom');
const customTextInput = document.getElementById('customTextInput');

// Form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    await generatePamphlet();
});

// Add feature functionality
function addFeature() {
    const container = document.getElementById('features-container');
    const featureInput = document.createElement('div');
    featureInput.className = 'feature-input';
    
    featureInput.innerHTML = `
        <input type="text" class="feature-input-field" placeholder="Enter a key feature...">
        <button type="button" class="remove-feature" onclick="removeFeature(this)">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(featureInput);
    
    // Show remove buttons for all features
    const removeButtons = container.querySelectorAll('.remove-feature');
    removeButtons.forEach(btn => btn.style.display = 'flex');
}

// Remove feature functionality
function removeFeature(button) {
    const featureInput = button.parentElement;
    const container = document.getElementById('features-container');
    
    // Don't remove if it's the last one
    if (container.children.length > 1) {
        featureInput.remove();
        
        // Hide remove buttons if only one feature left
        const remainingFeatures = container.querySelectorAll('.feature-input');
        if (remainingFeatures.length === 1) {
            remainingFeatures[0].querySelector('.remove-feature').style.display = 'none';
        }
    }
}

// Generate pamphlet
async function generatePamphlet() {
    const wasRegenerating = isRegenerating;
    try {
        // Show loading overlay
        showLoading();
        
        // Collect form data
        const formData = new FormData(form);
        const data = {
            product_name: formData.get('product_name'),
            description: formData.get('description'),
            tone: formData.get('tone'),
            target_audience: formData.get('target_audience'),
            call_to_action: formData.get('call_to_action'),
            color_scheme: formData.get('color_scheme'),
            style: formData.get('style'),
            image_prompt: formData.get('image_prompt'),
            image_source: document.querySelector('input[name="image_source"]:checked').value,
            key_features: [],
            regeneration_count: regenerationCount
        };
        
        // Add custom image if uploaded
        if (data.image_source === 'custom_upload' && customImageData) {
            data.custom_image = customImageData;
        }
        
        // Collect key features
        const featureInputs = document.querySelectorAll('.feature-input-field');
        featureInputs.forEach(input => {
            if (input.value.trim()) {
                data.key_features.push(input.value.trim());
            }
        });
        latestKeyFeatures = [...data.key_features];
        
        // Validate required fields
        if (!data.product_name || !data.description || !data.tone || !data.target_audience || !data.call_to_action) {
            throw new Error('Please fill in all required fields');
        }
        
        if (data.key_features.length === 0) {
            throw new Error('Please add at least one key feature');
        }
        
        // Disable generate button
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        
        // Make API request
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Display results
            displayResults(result);
            latestTextContent = result.text_content || null;
            if (result.text_content?.features) {
                latestKeyFeatures = result.text_content.features;
            }
        } else {
            throw new Error(result.error || 'Failed to generate pamphlet');
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error generating pamphlet: ' + error.message);
    } finally {
        // Hide loading overlay
        hideLoading();
        
        // Re-enable generate button
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate Pamphlet';
        if (!wasRegenerating) {
            regenerationCount = 0;
        }
        isRegenerating = false;
    }
}

// Display results
function displayResults(result) {
    finalImageData = result.image || '';
    layoutBaseImageData = result.layout_base_image || result.image || '';
    currentRemovals = {
        headline: false,
        tagline: false,
        description: false,
        call_to_action: false,
        custom: false
    };
    customTextLines = [];
    
    if (layoutBaseImageData) {
        pamphletImage.src = 'data:image/png;base64,' + layoutBaseImageData;
        pamphletImage.alt = 'Pamphlet Layout Preview';
        pamphletImage.style.display = 'block';
        originalImageData = layoutBaseImageData;
    } else {
        pamphletImage.style.display = 'none';
    }
    
    if (previewOverlay) {
        previewOverlay.style.display = 'block';
    }
    
    // Store filename for download
    currentFilename = result.filename;
    
    // Display generated text content
    if (result.text_content) {
        const headlineEl = document.getElementById('generatedHeadline');
        const taglineEl = document.getElementById('generatedTagline');
        const descriptionEl = document.getElementById('generatedDescription');
        const ctaEl = document.getElementById('generatedCTA');
        
        if (headlineEl) headlineEl.textContent = result.text_content.headline || '';
        if (taglineEl) taglineEl.textContent = result.text_content.tagline || '';
        if (descriptionEl) descriptionEl.textContent = result.text_content.description || '';
        if (ctaEl) ctaEl.textContent = result.text_content.call_to_action || '';
        if (customTextInput) customTextInput.value = '';
        if (hideHeadlineToggle) hideHeadlineToggle.checked = false;
        if (hideTaglineToggle) hideTaglineToggle.checked = false;
        if (hideDescriptionToggle) hideDescriptionToggle.checked = false;
        if (hideCtaToggle) hideCtaToggle.checked = false;
        if (hideCustomToggle) hideCustomToggle.checked = false;
        
        if (textContent) textContent.style.display = 'block';

        // Update live overlay
        if (previewHeadline) previewHeadline.textContent = (result.text_content.headline || '').toUpperCase();
        if (previewTagline) previewTagline.textContent = (result.text_content.tagline || '').toUpperCase();
        if (previewDescription) previewDescription.textContent = result.text_content.description || '';
        if (previewCTA) previewCTA.textContent = (result.text_content.call_to_action || '').toUpperCase();
    }
    
    // Show results container
    resultsContainer.style.display = 'block';
    
    // Initialize editing controls
    initializeEditingControls();
    applyPreviewChanges();
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

// Download pamphlet
function downloadPamphlet() {
    if (currentFilename) {
        window.open(`/download/${currentFilename}`, '_blank');
    } else {
        alert('No pamphlet to download');
    }
}

// Regenerate pamphlet
function regeneratePamphlet() {
    regenerationCount += 1;
    isRegenerating = true;
    generatePamphlet();
}

// Show loading overlay
function showLoading() {
    loadingOverlay.style.display = 'flex';
    
    // Simulate loading steps
    const steps = document.querySelectorAll('.step');
    let currentStep = 0;
    
    const stepInterval = setInterval(() => {
        if (currentStep < steps.length) {
            // Remove active from previous step
            if (currentStep > 0) {
                steps[currentStep - 1].classList.remove('active');
            }
            
            // Add active to current step
            steps[currentStep].classList.add('active');
            currentStep++;
        } else {
            clearInterval(stepInterval);
        }
    }, 2000);
}

// Hide loading overlay
function hideLoading() {
    loadingOverlay.style.display = 'none';
    
    // Reset steps
    const steps = document.querySelectorAll('.step');
    steps.forEach(step => step.classList.remove('active'));
}

// Initialize form with default features
document.addEventListener('DOMContentLoaded', function() {
    // Add initial feature input
    addFeature();
    
    // Set up form validation
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        field.addEventListener('input', validateForm);
    });
    
    // Initial validation
    validateForm();
    
    // Reset regeneration counter when user modifies inputs
    form.addEventListener('input', () => {
        if (!isRegenerating) {
            regenerationCount = 0;
        }
    });
    
    // Initialize editing controls (they might not exist yet, but we'll set up event delegation)
    setupEditingControls();
    
    // Set up image source switching
    setupImageSourceSwitching();
    
    // Set up custom image upload
    setupCustomImageUpload();

    // Set up removal toggles
    setupRemovalControls();

    // Set up custom text input
    if (customTextInput) {
        customTextInput.addEventListener('input', () => {
            const lines = customTextInput.value.split('\n').map(l => l.trim()).filter(Boolean);
            customTextLines = lines;
            applyPreviewChanges();
        });
    }
});

// Form validation
function validateForm() {
    const requiredFields = form.querySelectorAll('[required]');
    const features = document.querySelectorAll('.feature-input-field');
    const hasFeatures = Array.from(features).some(input => input.value.trim());
    
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
        }
    });
    
    if (!hasFeatures) {
        isValid = false;
    }
    
    generateBtn.disabled = !isValid;
}

// Auto-resize textarea
const descriptionTextarea = document.getElementById('description');
descriptionTextarea.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
});

// Add smooth scrolling for better UX
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to generate
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        if (!generateBtn.disabled) {
            generatePamphlet();
        }
    }
});

// Add feature input on Enter key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.target.classList.contains('feature-input-field')) {
        e.preventDefault();
        addFeature();
        
        // Focus on the new input
        const newInput = document.querySelector('.feature-input:last-child .feature-input-field');
        if (newInput) {
            newInput.focus();
        }
    }
});

// Add tooltips for better UX
function addTooltip(element, text) {
    element.setAttribute('title', text);
}

// Add tooltips to form elements
document.addEventListener('DOMContentLoaded', function() {
    const productNameInput = document.getElementById('product_name');
    addTooltip(productNameInput, 'Enter a catchy, memorable product name');
    
    const descriptionTextarea = document.getElementById('description');
    addTooltip(descriptionTextarea, 'Provide a detailed description of your product and its benefits');
    
    const toneSelect = document.getElementById('tone');
    addTooltip(toneSelect, 'Choose the tone that best matches your brand and target audience');
    
    const targetAudienceInput = document.getElementById('target_audience');
    addTooltip(targetAudienceInput, 'Describe your ideal customers (e.g., "young professionals", "health-conscious families")');
    
    const ctaInput = document.getElementById('call_to_action');
    addTooltip(ctaInput, 'Create an action-oriented message that encourages customers to take action');
});

// Add animation to form sections
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe form sections
document.addEventListener('DOMContentLoaded', function() {
    const formSections = document.querySelectorAll('.form-section');
    formSections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });
});

// Editing Functions
function setupEditingControls() {
    // Use event delegation for dynamically created elements
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('control-tab')) {
            switchTab(e.target.dataset.tab);
        }
        if (e.target.classList.contains('crop-btn')) {
            document.querySelectorAll('.crop-btn').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            currentEdits.imageCrop = e.target.dataset.crop;
            applyPreviewChanges();
        }
    });
    
    // Set up range sliders with event delegation
    document.addEventListener('input', function(e) {
        if (e.target.id === 'backgroundOpacity') {
            currentEdits.backgroundOpacity = e.target.value;
            const opacityValue = document.getElementById('opacityValue');
            if (opacityValue) opacityValue.textContent = e.target.value + '%';
            applyPreviewChanges();
        }
        if (e.target.id === 'headlineSize') {
            currentEdits.headlineSize = e.target.value;
            const headlineSizeValue = document.getElementById('headlineSizeValue');
            if (headlineSizeValue) headlineSizeValue.textContent = e.target.value + 'px';
            applyPreviewChanges();
        }
        if (e.target.id === 'bodySize') {
            currentEdits.bodySize = e.target.value;
            const bodySizeValue = document.getElementById('bodySizeValue');
            if (bodySizeValue) bodySizeValue.textContent = e.target.value + 'px';
            applyPreviewChanges();
        }
        if (e.target.id === 'filterIntensity') {
            currentEdits.filterIntensity = e.target.value;
            const filterIntensityValue = document.getElementById('filterIntensityValue');
            if (filterIntensityValue) filterIntensityValue.textContent = e.target.value + '%';
            applyPreviewChanges();
        }
        if (e.target.id === 'shadowIntensity') {
            currentEdits.shadowIntensity = e.target.value;
            const shadowIntensityValue = document.getElementById('shadowIntensityValue');
            if (shadowIntensityValue) shadowIntensityValue.textContent = e.target.value + '%';
            applyPreviewChanges();
        }
        if (e.target.id === 'borderRadius') {
            currentEdits.borderRadius = e.target.value;
            const borderRadiusValue = document.getElementById('borderRadiusValue');
            if (borderRadiusValue) borderRadiusValue.textContent = e.target.value + 'px';
            applyPreviewChanges();
        }
        if (e.target.id === 'textShadow') {
            currentEdits.textShadow = e.target.value;
            const textShadowValue = document.getElementById('textShadowValue');
            if (textShadowValue) textShadowValue.textContent = e.target.value + '%';
            applyPreviewChanges();
        }
        if (e.target.id === 'overallBrightness') {
            currentEdits.overallBrightness = e.target.value;
            const overallBrightnessValue = document.getElementById('overallBrightnessValue');
            if (overallBrightnessValue) overallBrightnessValue.textContent = e.target.value + '%';
            applyPreviewChanges();
        }
    });
    
    // Set up select dropdowns with event delegation
    document.addEventListener('change', function(e) {
        if (e.target.id === 'pamphletSize') {
            handleSizeChange();
        }
        if (e.target.id === 'layoutStyle') {
            currentEdits.layout = e.target.value;
            applyPreviewChanges();
        }
        if (e.target.id === 'textPlacement') {
            currentEdits.textPlacement = e.target.value;
            applyPreviewChanges();
        }
        if (e.target.id === 'headlineFont') {
            currentEdits.headlineFont = e.target.value;
            applyPreviewChanges();
        }
        if (e.target.id === 'headlineColor') {
            currentEdits.headlineColor = e.target.value;
            applyPreviewChanges();
        }
        if (e.target.id === 'bodyFont') {
            currentEdits.bodyFont = e.target.value;
            applyPreviewChanges();
        }
        if (e.target.id === 'bodyColor') {
            currentEdits.bodyColor = e.target.value;
            applyPreviewChanges();
        }
        if (e.target.id === 'ctaBgColor') {
            currentEdits.ctaBgColor = e.target.value;
            applyPreviewChanges();
        }
        if (e.target.id === 'ctaTextColor') {
            currentEdits.ctaTextColor = e.target.value;
            applyPreviewChanges();
        }
        if (e.target.id === 'imageFilter') {
            currentEdits.imageFilter = e.target.value;
            const filterIntensityGroup = document.getElementById('filterIntensityGroup');
            if (filterIntensityGroup) {
                if (e.target.value === 'none') {
                    filterIntensityGroup.style.display = 'none';
                } else {
                    filterIntensityGroup.style.display = 'block';
                }
            }
            applyPreviewChanges();
        }
        if (e.target.id === 'imagePosition') {
            currentEdits.imagePosition = e.target.value;
            applyPreviewChanges();
        }
    });
    
    // Set up custom size inputs
    document.addEventListener('input', function(e) {
        if (e.target.id === 'customWidth' || e.target.id === 'customHeight') {
            handleCustomSizeChange();
        }
    });
}

function initializeEditingControls() {
    // This function is called when results are displayed
    // The controls are already set up via event delegation
    console.log('Editing controls initialized');
}

function switchTab(tabName) {
    // Hide all panels
    document.querySelectorAll('.control-panel').forEach(panel => {
        panel.style.display = 'none';
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.control-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected panel
    document.getElementById(tabName + '-panel').style.display = 'block';
    
    // Add active class to selected tab
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
}

function handleSizeChange() {
    const pamphletSize = document.getElementById('pamphletSize');
    const customSizeGroup = document.getElementById('customSizeGroup');
    
    if (pamphletSize.value === 'custom') {
        customSizeGroup.style.display = 'block';
    } else {
        customSizeGroup.style.display = 'none';
        const dimensions = pamphletSize.value.split('x');
        currentEdits.size.width = parseInt(dimensions[0]);
        currentEdits.size.height = parseInt(dimensions[1]);
        applyPreviewChanges();
    }
}

function handleCustomSizeChange() {
    const customWidth = document.getElementById('customWidth');
    const customHeight = document.getElementById('customHeight');
    
    if (customWidth.value && customHeight.value) {
        currentEdits.size.width = parseInt(customWidth.value);
        currentEdits.size.height = parseInt(customHeight.value);
        applyPreviewChanges();
    }
}

function applyPreviewChanges() {
    if (!originalImageData) return;
    
    let previewWidth = currentEdits.size.width;
    let previewHeight = currentEdits.size.height;
    if (currentEdits.imageCrop === 'square') {
        previewWidth = 1000;
        previewHeight = 1000;
    } else if (currentEdits.imageCrop === 'portrait') {
        previewWidth = 1200;
        previewHeight = 1600;
    } else if (currentEdits.imageCrop === 'landscape') {
        previewWidth = 1600;
        previewHeight = 1200;
    }
    const aspectRatio = previewWidth / previewHeight;
    if (previewContainer) {
        previewContainer.style.aspectRatio = `${previewWidth}/${previewHeight}`;
    }
    if (pamphletImage) {
        pamphletImage.style.aspectRatio = `${previewWidth}/${previewHeight}`;
        pamphletImage.style.objectFit = currentEdits.imageCrop === 'none' ? 'contain' : 'cover';
        const positionMap = {
            top: '50% 10%',
            bottom: '50% 90%',
            left: '10% 50%',
            right: '90% 50%',
            center: '50% 50%'
        };
        pamphletImage.style.objectPosition = positionMap[currentEdits.imagePosition] || '50% 50%';
    }

    // Apply CSS filters and effects to the preview
    let filterString = '';
    
    // Image filters
    if (currentEdits.imageFilter !== 'none') {
        switch (currentEdits.imageFilter) {
            case 'brightness':
                filterString += `brightness(${100 + parseInt(currentEdits.filterIntensity)}%) `;
                break;
            case 'contrast':
                filterString += `contrast(${100 + parseInt(currentEdits.filterIntensity)}%) `;
                break;
            case 'saturate':
                filterString += `saturate(${100 + parseInt(currentEdits.filterIntensity)}%) `;
                break;
            case 'blur':
                filterString += `blur(${parseInt(currentEdits.filterIntensity) / 10}px) `;
                break;
            case 'sepia':
                filterString += `sepia(${currentEdits.filterIntensity}%) `;
                break;
            case 'grayscale':
                filterString += `grayscale(${currentEdits.filterIntensity}%) `;
                break;
        }
    }
    
    // Overall brightness
    filterString += `brightness(${currentEdits.overallBrightness}%) `;
    
    // Apply filters to image
    pamphletImage.style.filter = filterString;
    
    // Apply border radius
    pamphletImage.style.borderRadius = currentEdits.borderRadius + 'px';
    
    // Apply shadow
    if (currentEdits.shadowIntensity > 0) {
        pamphletImage.style.boxShadow = `0 10px 30px rgba(0,0,0,${currentEdits.shadowIntensity / 100})`;
    } else {
        pamphletImage.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)';
    }
    
    // Apply background opacity overlay
    previewOverlay.style.backgroundColor = `rgba(0,0,0,${(100 - currentEdits.backgroundOpacity) / 100})`;

    // Apply text styling live
    if (previewHeadline) {
        previewHeadline.style.color = currentEdits.headlineColor;
        previewHeadline.style.fontSize = `${currentEdits.headlineSize}px`;
        previewHeadline.style.fontFamily = currentEdits.headlineFont.replace('-Bold','');
        previewHeadline.style.textShadow = currentEdits.textShadow > 0 ? `0 3px 8px rgba(0,0,0,${currentEdits.textShadow/100})` : 'none';
        previewHeadline.style.display = currentRemovals.headline ? 'none' : 'block';
    }
    if (previewDescription) {
        previewDescription.style.color = currentEdits.bodyColor;
        previewDescription.style.fontSize = `${currentEdits.bodySize}px`;
        previewDescription.style.fontFamily = currentEdits.bodyFont;
        previewDescription.style.textShadow = currentEdits.textShadow > 0 ? `0 2px 6px rgba(0,0,0,${currentEdits.textShadow/100})` : 'none';
        previewDescription.style.maxWidth = '900px';
        previewDescription.style.display = currentRemovals.description ? 'none' : 'block';
    }
    if (previewTagline) {
        previewTagline.style.color = currentEdits.bodyColor;
        previewTagline.style.fontSize = `${Math.max(18, Math.min(48, currentEdits.bodySize + 4))}px`;
        previewTagline.style.fontFamily = currentEdits.bodyFont;
        previewTagline.style.textShadow = currentEdits.textShadow > 0 ? `0 2px 6px rgba(0,0,0,${currentEdits.textShadow/100})` : 'none';
        previewTagline.style.display = currentRemovals.tagline ? 'none' : 'block';
    }
    if (previewCTA) {
        previewCTA.style.backgroundColor = currentEdits.ctaBgColor;
        previewCTA.style.color = currentEdits.ctaTextColor;
        previewCTA.style.borderRadius = `${currentEdits.borderRadius}px`;
        previewCTA.style.boxShadow = currentEdits.shadowIntensity > 0 ? `0 6px 18px rgba(0,0,0,${Math.max(0.25, currentEdits.shadowIntensity/100)})` : 'none';
        previewCTA.style.display = currentRemovals.call_to_action ? 'none' : 'inline-block';
    }
    if (previewCustom) {
        previewCustom.innerHTML = '';
        if (!currentRemovals.custom && customTextLines.length) {
            customTextLines.forEach(line => {
                const div = document.createElement('div');
                div.textContent = line;
                previewCustom.appendChild(div);
            });
            previewCustom.style.display = 'block';
        } else {
            previewCustom.style.display = 'none';
        }
    }

    if (overlayContent) {
        const placementMap = {
            top: 'flex-start',
            middle: 'center',
            bottom: 'flex-end'
        };
        overlayContent.style.justifyContent = placementMap[currentEdits.textPlacement] || 'flex-start';
        const alignMap = {
            'centered': 'center',
            'left-aligned': 'flex-start',
            'right-aligned': 'flex-end',
            'split': 'flex-start'
        };
        overlayContent.style.alignItems = alignMap[currentEdits.layout] || 'center';
        const textAlign = currentEdits.layout === 'right-aligned' ? 'right' : currentEdits.layout === 'left-aligned' || currentEdits.layout === 'split' ? 'left' : 'center';
    [previewHeadline, previewDescription, previewTagline, previewCTA, previewCustom].forEach(el => {
            if (el) {
                el.style.textAlign = textAlign;
            }
        });
    }
}

function saveEditedPamphlet() {
    if (!originalImageData) {
        alert('No pamphlet to save');
        return;
    }
    
    // Send edit data to backend for processing
    fetch('/edit-pamphlet', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            originalImage: layoutBaseImageData || originalImageData,
            edits: currentEdits,
            filename: currentFilename,
            // send text content and styles so server can render text
            textContent: {
                headline: document.getElementById('generatedHeadline')?.textContent || '',
                tagline: document.getElementById('generatedTagline')?.textContent || '',
                description: document.getElementById('generatedDescription')?.textContent || '',
                call_to_action: document.getElementById('generatedCTA')?.textContent || '',
                features: latestKeyFeatures || [],
                customText: customTextLines || [],
                removeLines: currentRemovals
            }
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            finalImageData = result.editedImage;
            if (result.layoutBaseImage) {
                layoutBaseImageData = result.layoutBaseImage;
            }
            const previewSource = layoutBaseImageData || finalImageData;
            if (previewSource) {
                pamphletImage.src = 'data:image/png;base64,' + previewSource;
                pamphletImage.style.display = 'block';
                originalImageData = previewSource;
            }
            currentFilename = result.filename;
            alert('Pamphlet saved successfully!');
        } else {
            alert('Error saving pamphlet: ' + result.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error saving pamphlet: ' + error.message);
    });
}

function resetEdits() {
    if (!originalImageData) return;
    
    // Reset all controls to default values
    currentEdits = {
        size: { width: 1200, height: 1600 },
        layout: 'centered',
        textPlacement: 'top',
        backgroundOpacity: 80,
        headlineFont: 'Arial-Bold',
        headlineSize: 72,
        headlineColor: '#ffffff',
        bodyFont: 'Arial',
        bodySize: 28,
        bodyColor: '#ffffff',
        ctaBgColor: '#ff6464',
        ctaTextColor: '#ffffff',
        imageFilter: 'none',
        filterIntensity: 50,
        imageCrop: 'none',
        imagePosition: 'center',
        shadowIntensity: 0,
        borderRadius: 12,
        textShadow: 0,
        overallBrightness: 100
    };
    currentRemovals = {
        headline: false,
        tagline: false,
        description: false,
        call_to_action: false,
        custom: false
    };
    customTextLines = [];
    
    // Reset form controls
    document.getElementById('pamphletSize').value = '1200x1600';
    document.getElementById('customSizeGroup').style.display = 'none';
    document.getElementById('layoutStyle').value = 'centered';
    document.getElementById('textPlacement').value = 'top';
    document.getElementById('backgroundOpacity').value = 80;
    document.getElementById('opacityValue').textContent = '80%';
    document.getElementById('headlineFont').value = 'Arial-Bold';
    document.getElementById('headlineSize').value = 72;
    document.getElementById('headlineSizeValue').textContent = '72px';
    document.getElementById('headlineColor').value = '#ffffff';
    document.getElementById('bodyFont').value = 'Arial';
    document.getElementById('bodySize').value = 28;
    document.getElementById('bodySizeValue').textContent = '28px';
    document.getElementById('bodyColor').value = '#ffffff';
    document.getElementById('ctaBgColor').value = '#ff6464';
    document.getElementById('ctaTextColor').value = '#ffffff';
    document.getElementById('imageFilter').value = 'none';
    document.getElementById('filterIntensityGroup').style.display = 'none';
    document.getElementById('filterIntensity').value = 50;
    document.getElementById('filterIntensityValue').textContent = '50%';
    document.querySelectorAll('.crop-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector('[data-crop="none"]').classList.add('active');
    document.getElementById('imagePosition').value = 'center';
    document.getElementById('shadowIntensity').value = 0;
    document.getElementById('shadowIntensityValue').textContent = '0%';
    document.getElementById('borderRadius').value = 12;
    document.getElementById('borderRadiusValue').textContent = '12px';
    document.getElementById('textShadow').value = 0;
    document.getElementById('textShadowValue').textContent = '0%';
    document.getElementById('overallBrightness').value = 100;
    document.getElementById('overallBrightnessValue').textContent = '100%';
    document.getElementById('toggleHeadline').checked = false;
    document.getElementById('toggleTagline').checked = false;
    document.getElementById('toggleDescription').checked = false;
    document.getElementById('toggleCTA').checked = false;
    document.getElementById('toggleCustom').checked = false;
    if (customTextInput) {
        customTextInput.value = '';
    }
    
    // Reset image display
    pamphletImage.src = 'data:image/png;base64,' + originalImageData;
    pamphletImage.style.filter = '';
    pamphletImage.style.borderRadius = '12px';
    pamphletImage.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)';
    previewOverlay.style.backgroundColor = 'rgba(0,0,0,0.2)';
    
    alert('All edits have been reset to default values');
}

// Image Upload Functions
function setupImageSourceSwitching() {
    document.addEventListener('change', function(e) {
        if (e.target.name === 'image_source') {
            const aiImageGroup = document.getElementById('aiImageGroup');
            const customImageGroup = document.getElementById('customImageGroup');
            
            if (e.target.value === 'ai_generated') {
                aiImageGroup.style.display = 'block';
                customImageGroup.style.display = 'none';
            } else if (e.target.value === 'custom_upload') {
                aiImageGroup.style.display = 'none';
                customImageGroup.style.display = 'block';
            }
        }
    });
}

function setupCustomImageUpload() {
    const customImageInput = document.getElementById('custom_image');
    if (customImageInput) {
        customImageInput.addEventListener('change', handleImageUpload);
    }
}

function setupRemovalControls() {
    const map = [
        { el: hideHeadlineToggle, key: 'headline' },
        { el: hideTaglineToggle, key: 'tagline' },
        { el: hideDescriptionToggle, key: 'description' },
        { el: hideCtaToggle, key: 'call_to_action' },
        { el: hideCustomToggle, key: 'custom' },
    ];
    map.forEach(({ el, key }) => {
        if (el) {
            el.addEventListener('change', () => {
                currentRemovals[key] = el.checked;
                applyPreviewChanges();
            });
        }
    });
}

function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
        alert('Please select a valid image file (JPG, PNG, GIF)');
        return;
    }
    
    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
    }
    
    // Convert to base64
    const reader = new FileReader();
    reader.onload = function(e) {
        customImageData = e.target.result.split(',')[1]; // Remove data:image/...;base64, prefix
        document.getElementById('fileName').textContent = file.name;
        
        // Show preview
        const preview = document.getElementById('imagePreview');
        const previewImg = document.getElementById('previewImage');
        previewImg.src = e.target.result;
        preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

function removeCustomImage() {
    customImageData = '';
    document.getElementById('custom_image').value = '';
    document.getElementById('fileName').textContent = 'No file selected';
    document.getElementById('imagePreview').style.display = 'none';
}
