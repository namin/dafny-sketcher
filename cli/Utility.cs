using System.Linq;
using Microsoft.Dafny;

namespace DafnySketcherCli {
  public static class Utility {
    public static Method? GetMethodByName(Microsoft.Dafny.Program prog, string name) {
      return prog.DefaultModuleDef
        .TopLevelDecls
        .OfType<TopLevelDeclWithMembers>()
        .SelectMany(d => d.Members.OfType<Method>())
        .FirstOrDefault(m => m.Name == name);
    }
  }
}