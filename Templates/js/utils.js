/**
 * SpeakWell Utilities
 * Common functions and constants used across the application.
 */

const ACCURACY_LEVELS = [
    { threshold: 90, label: 'Excellent 90-100%', color: '#22C55E' },
    { threshold: 85, label: 'Very Good 85-89%', color: '#1D4ED8' },
    { threshold: 75, label: 'Good 75-84%', color: '#38BDF8' },
    { threshold: 60, label: 'Average 60-74%', color: '#EAB308' },
    { threshold: 50, label: 'Below Avg 50-59%', color: '#F97316' },
    { threshold: 30, label: 'Needs Practice 30-49%', color: '#FCA5A5' },
    { threshold: 1,  label: 'Beginner 1-29%', color: '#800000' },
    { threshold: 0,  label: 'No Data 0%', color: '#94A3B8' }
];

/**
 * Returns the color associated with a given accuracy percentage.
 * @param {number} accuracy - The accuracy percentage (0-100).
 * @returns {string} - The hex color code.
 */
function getAccuracyColor(accuracy) {
    const level = ACCURACY_LEVELS.find(l => accuracy >= l.threshold);
    return level ? level.color : '#94A3B8';
}

// Export if using modules, but for simple script inclusion, they are global.
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ACCURACY_LEVELS, getAccuracyColor };
}
