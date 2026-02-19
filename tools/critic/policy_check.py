"""Policy adherence scanner: FORBIDDEN pattern detection.

Discovers FORBIDDEN patterns from architectural policy files (arch_*.md)
and scans implementation files for violations.
"""

import os
import re


def discover_forbidden_patterns(features_dir):
    """Scan arch_*.md files for FORBIDDEN: lines.

    Returns dict: {policy_file: [{"pattern": str, "line": int}]}
    """
    patterns = {}

    if not os.path.isdir(features_dir):
        return patterns

    for fname in sorted(os.listdir(features_dir)):
        if not (fname.startswith('arch_') and fname.endswith('.md')):
            continue

        filepath = os.path.join(features_dir, fname)
        file_patterns = []

        try:
            with open(filepath, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    stripped = line.strip()
                    # Match lines like: FORBIDDEN: some_pattern
                    # or: `FORBIDDEN: some_pattern`
                    # or within list items: * FORBIDDEN: some_pattern
                    match = re.search(r'FORBIDDEN:\s*(.+)', stripped)
                    if match:
                        pattern_text = match.group(1).strip()
                        # Remove trailing markdown formatting
                        pattern_text = pattern_text.rstrip('`').strip()
                        if pattern_text:
                            file_patterns.append({
                                'pattern': pattern_text,
                                'line': line_num,
                            })
        except (IOError, OSError):
            continue

        if file_patterns:
            patterns[fname] = file_patterns

    return patterns


def get_feature_prerequisites(feature_content):
    """Extract prerequisite references from feature file content.

    Returns list of referenced filenames (e.g., ['arch_critic_policy.md']).
    """
    prereqs = []
    for line in feature_content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('> Prerequisite:'):
            # Extract filename references
            text = stripped[len('> Prerequisite:'):].strip()
            # Match arch_*.md patterns
            matches = re.findall(r'(arch_\w+\.md)', text)
            prereqs.extend(matches)
            # Also match features/arch_*.md patterns
            matches = re.findall(r'features/(arch_\w+\.md)', text)
            for m in matches:
                if m not in prereqs:
                    prereqs.append(m)
    return prereqs


def discover_implementation_files(project_root, feature_stem, tools_root='tools'):
    """Find implementation files for a feature.

    Looks in tool directories that might correspond to the feature.
    Returns list of absolute file paths.
    """
    impl_files = []

    # Map feature stems to likely tool directories
    # e.g., 'critic_tool' -> 'critic', 'cdd_status_monitor' -> 'cdd'
    possible_dirs = set()
    possible_dirs.add(feature_stem)

    # Strip common suffixes
    for suffix in ('_tool', '_status_monitor', '_generator', '_sync',
                   '_bootstrap'):
        if feature_stem.endswith(suffix):
            possible_dirs.add(feature_stem[:len(feature_stem) - len(suffix)])

    tools_abs = os.path.join(project_root, tools_root)
    if not os.path.isdir(tools_abs):
        return impl_files

    for entry in os.listdir(tools_abs):
        tool_dir = os.path.join(tools_abs, entry)
        if not os.path.isdir(tool_dir):
            continue

        # Check if this tool dir matches the feature
        if entry in possible_dirs or feature_stem.startswith(entry):
            for fname in os.listdir(tool_dir):
                fpath = os.path.join(tool_dir, fname)
                if os.path.isfile(fpath) and not fname.startswith('.'):
                    impl_files.append(fpath)

    return impl_files


def scan_file_for_violations(filepath, patterns):
    """Scan a single file for FORBIDDEN pattern matches.

    Args:
        filepath: absolute path to the file to scan
        patterns: list of pattern strings

    Returns list of violations: [{"pattern": str, "file": str, "line": int, "text": str}]
    """
    violations = []

    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except (IOError, OSError, UnicodeDecodeError):
        return violations

    for pattern_text in patterns:
        try:
            regex = re.compile(pattern_text)
        except re.error:
            # Treat as literal string match if not valid regex
            regex = re.compile(re.escape(pattern_text))

        for line_num, line in enumerate(lines, 1):
            if regex.search(line):
                violations.append({
                    'pattern': pattern_text,
                    'file': filepath,
                    'line': line_num,
                    'text': line.strip(),
                })

    return violations


def run_policy_check(feature_content, project_root, feature_stem,
                     features_dir=None, tools_root='tools'):
    """Run full policy adherence check for a feature.

    Args:
        feature_content: raw feature file text
        project_root: absolute path to project root
        feature_stem: feature file stem (e.g., 'critic_tool')
        features_dir: absolute path to features directory (default: project_root/features)
        tools_root: relative path to tools directory

    Returns:
        dict with 'status', 'violations', 'detail'
    """
    if features_dir is None:
        features_dir = os.path.join(project_root, 'features')

    # Find which policies this feature is anchored to
    prereqs = get_feature_prerequisites(feature_content)
    if not prereqs:
        return {
            'status': 'PASS',
            'violations': [],
            'detail': 'No policy prerequisites defined.',
        }

    # Get FORBIDDEN patterns from referenced policies
    all_patterns = discover_forbidden_patterns(features_dir)
    relevant_patterns = []
    for prereq_file in prereqs:
        if prereq_file in all_patterns:
            for p in all_patterns[prereq_file]:
                relevant_patterns.append(p['pattern'])

    if not relevant_patterns:
        return {
            'status': 'PASS',
            'violations': [],
            'detail': 'No FORBIDDEN patterns in referenced policies.',
        }

    # Discover implementation files
    impl_files = discover_implementation_files(
        project_root, feature_stem, tools_root
    )

    if not impl_files:
        return {
            'status': 'PASS',
            'violations': [],
            'detail': 'No implementation files found to scan.',
        }

    # Scan for violations
    all_violations = []
    for fpath in impl_files:
        violations = scan_file_for_violations(fpath, relevant_patterns)
        # Store relative paths for readability
        for v in violations:
            v['file'] = os.path.relpath(v['file'], project_root)
        all_violations.extend(violations)

    if all_violations:
        detail = f'{len(all_violations)} FORBIDDEN violation(s) detected'
        return {
            'status': 'FAIL',
            'violations': all_violations,
            'detail': detail,
        }

    return {
        'status': 'PASS',
        'violations': [],
        'detail': f'Scanned {len(impl_files)} file(s), no violations.',
    }
