# Contributing to BirdNET Batch Analysis

Thank you for your interest in contributing! This project aims to make bioacoustic analysis accessible to researchers and bird monitoring projects worldwide.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- **Description**: Clear description of the problem
- **Steps to Reproduce**: Minimal steps to reproduce the issue
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, Jupyter version
- **Audio File Details**: Duration, format, sample rate (if relevant)

### Suggesting Enhancements

We welcome feature suggestions! Please open an issue with:
- **Use Case**: Describe the research scenario
- **Proposed Solution**: How you envision it working
- **Alternatives**: Other approaches you've considered
- **Examples**: Links to similar features in other tools

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**:
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed
4. **Test your changes**:
   - Run the notebook with sample data
   - Verify outputs (CSVs, labels, visualizations)
5. **Commit with clear messages**:
   ```
   Add support for MP3 files in BirdNET analysis

   - Updated audio loading to handle MP3 format
   - Added ffmpeg dependency check
   - Updated README with MP3 requirements
   ```
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Open a Pull Request**

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8
- **Jupyter Notebooks**: Keep cells focused and well-documented
- **Comments**: Explain *why*, not just *what*
- **Variable Names**: Use descriptive names (`audio_file_path` not `afp`)

### Adding New Features

#### New Analysis Methods
If adding acoustic analysis features:
- Document the method with academic references
- Provide parameter defaults that work for most bird species
- Include examples in docstrings

#### New Export Formats
If adding export formats (e.g., Praat, Sonic Visualiser):
- Research the format specification thoroughly
- Add format documentation to README
- Provide example files in `shared/examples/`

#### Performance Improvements
- Profile before optimizing
- Document performance gains in PR
- Ensure backward compatibility

### Testing

Currently, this project uses manual testing with example files. If you'd like to help add automated tests:
- Use `pytest` for unit tests
- Add sample audio files to `tests/fixtures/`
- Test with various audio formats and durations

## Community Guidelines

- **Be Respectful**: This is a research tool used by students and professionals
- **Be Patient**: Maintainers may be in the field collecting data!
- **Be Collaborative**: Share your use cases and results
- **Cite Properly**: If using for research, cite both this tool and BirdNET

## Research Contributions

If you use this tool in published research:
- Please cite using `CITATION.cff`
- Share your paper in Discussions
- Consider contributing your improvements back

## Documentation

Good documentation helps everyone:
- Update README if you change functionality
- Add inline comments for complex code
- Include examples for new features
- Update troubleshooting section for known issues

## Questions?

- **Usage Questions**: Open a Discussion
- **Bug Reports**: Open an Issue
- **Feature Requests**: Open an Issue with `enhancement` label
- **Pull Requests**: Reference related issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Acknowledgments

This project builds on:
- **BirdNET** (Kahl et al., 2021) - Cornell Lab of Ornithology
- **Raven Pro** - Cornell Lab of Ornithology
- **librosa** - Audio analysis library
- **NTNU** - Norwegian University of Science and Technology

Thank you for helping make bioacoustic research more accessible!
