using System.Linq;
using Microsoft.Dafny;

namespace DafnySketcherCli {
  public static class Utility {
    public static Method? GetMethodByName(Microsoft.Dafny.Program resolvedProgram, string name) {
      if (resolvedProgram.DefaultModuleDef is DefaultModuleDefinition defaultModule) {
        foreach (var (member, _) in defaultModule.AccessibleMembers)
        {
          var method = member as Method;
          if (method != null && method.Name == name) {
            return method;
          }
        }
      }
      return null;
    }

    public static Method GetEnclosingMethodByPosition(Microsoft.Dafny.Program resolvedProgram, int line, int col) {
      if (resolvedProgram.DefaultModuleDef is DefaultModuleDefinition defaultModule) {
        foreach (var (member, _) in defaultModule.AccessibleMembers)
        {
          var method = member as Method;
          if (method != null && IsPositionInRange(method.StartToken, method.EndToken, line, col)) {
            return method;
          }
        }
      }
      return null;
    }
    private static bool IsPositionInRange(IOrigin startToken, IOrigin endToken, int line, int col) {
      return line >= startToken.line && line <= endToken.line &&
            (line != startToken.line || col >= startToken.col) &&
            (line != endToken.line || col <= endToken.col);
    }

    /// <summary>
    /// Returns a copy of the source with the method body emptied.
    /// This is useful for induction sketchers that need to see an empty body
    /// to make the correct choice between structural and rule induction.
    /// </summary>
    public static string EmptyMethodBody(string source, Method method) {
      if (method.Body == null) {
        return source; // Already empty
      }

      // Use the exact token positions to locate the body content
      var bodyStartToken = method.Body.StartToken;
      var bodyEndToken = method.Body.EndToken;

      // Calculate character positions in the source string
      var lines = source.Split('\n');
      int startPos = 0;

      // Find the start position of the body's opening brace
      for (int i = 0; i < bodyStartToken.line - 1; i++) {
        startPos += lines[i].Length + 1; // +1 for newline
      }
      startPos += bodyStartToken.col;

      // Find the end position of the body's closing brace
      int endPos = 0;
      for (int i = 0; i < bodyEndToken.line - 1; i++) {
        endPos += lines[i].Length + 1; // +1 for newline
      }
      endPos += bodyEndToken.col;

      // Build result: everything before body + "{" + "\n" + "}" + everything after body
      var result = new System.Text.StringBuilder();
      result.Append(source.Substring(0, startPos)); // Everything before the body opening brace
      result.Append("{\n\n}"); // Empty body
      if (endPos + 1 < source.Length) {
        result.Append(source.Substring(endPos + 1)); // Everything after the body closing brace
      }

      return result.ToString();
    }
  }
}