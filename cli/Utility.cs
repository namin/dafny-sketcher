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
  }
}