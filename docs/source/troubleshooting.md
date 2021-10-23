# Troubleshooting:

##. Elementree issues

:::{code-block}
    raise TypeError('expected an Element, not %s' % type(e).name)
    TypeError: expected an Element, not Element
:::

**Solutions**:
Downgrade python to 3.7.9.